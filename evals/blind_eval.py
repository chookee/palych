#!/usr/bin/env python3
"""Offline paired evaluation: prepare, lock masked judgments, then unblind."""
import argparse
import hashlib
import json
import random
import secrets
from collections import Counter
from pathlib import Path

DIMENSIONS = {
    "answer": "0: misses request; 1: answer present but hard to find; 2: main answer easy to find",
    "terms": "0: confusing terms or referents; 1: some avoidable ambiguity; 2: terms and referents clear",
    "connections": "0: missing reasoning; 1: reader must infer a useful link; 2: necessary links explicit",
    "structure": "0: obstructs reading; 1: usable with avoidable clutter; 2: structure fits the task",
    "language": "0: hard to follow or disrespectful; 1: some unnatural wording; 2: natural for stated reader",
}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_new(path, data):
    # Exclusive creation prevents accidental replacement of evidence.
    with Path(path).open("x", encoding="utf-8") as stream:
        json.dump(data, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def unknown_fields(value, path):
    if isinstance(value, str) and value.strip().lower() in ("unknown", "unavailable", "not exposed"):
        raise ValueError("Represent unavailable generation fields as null, not placeholder strings")
    if value is None:
        return [path]
    if isinstance(value, dict):
        return [item for key, child in value.items() for item in unknown_fields(child, f"{path}.{key}")]
    if isinstance(value, list):
        return [item for index, child in enumerate(value) for item in unknown_fields(child, f"{path}[{index}]")]
    return []


def check_manifest(manifest, skill, prompts, exploratory=False):
    for key in ("model", "settings", "tools", "base_instructions_sha256", "skill_sha256", "prompts_sha256", "verified", "verification_note"):
        require(key in manifest, f"Manifest missing {key}")
    require(manifest["verified"] is True, "Generation metadata must be explicitly verified")
    model = manifest["model"]
    require((exploratory and model is None) or (isinstance(model, str) and model.strip() and model.strip().lower() not in ("unknown", "unavailable", "not exposed")), "An observed model identifier is required; use null only in an exploratory pilot")
    require(isinstance(manifest["settings"], dict) or (exploratory and manifest["settings"] is None), "settings must be observed; use null only in an exploratory pilot")
    unknown = unknown_fields({key: manifest[key] for key in ("model", "settings", "base_instructions_sha256")}, "generation")
    require(exploratory or not unknown, "Unknown generation fields require an exploratory pilot")
    if exploratory:
        observed = manifest.get("observed_host_configuration")
        require(isinstance(observed, str) and observed.strip(), "Exploratory pilot requires observed_host_configuration text")
    require(isinstance(manifest["tools"], list), "tools must list identical allowed tools")
    require(isinstance(manifest["verification_note"], str) and manifest["verification_note"].strip(), "Explain how metadata was verified")
    for key in ("base_instructions_sha256", "skill_sha256", "prompts_sha256"):
        value = manifest[key]
        if exploratory and key == "base_instructions_sha256" and value is None:
            continue
        require(isinstance(value, str) and len(value) == 64 and all(c in "0123456789abcdef" for c in value), f"Invalid {key}")
    require(manifest["skill_sha256"] == digest(skill), "Skill hash does not match supplied file")
    require(manifest["prompts_sha256"] == digest(prompts), "Prompt hash does not match supplied file")
    keys = ("model", "settings", "tools", "base_instructions_sha256")
    if exploratory:
        keys += ("observed_host_configuration",)
    return {key: manifest[key] for key in keys}


def prepare(responses, manifest, prompts, skill, output, repetitions=3, pilot=False, limitation="", seed=None, exploratory=False):
    require(not exploratory or pilot, "Exploratory mode is allowed only with --pilot")
    metadata = check_manifest(manifest, skill, prompts, exploratory)
    require(type(repetitions) is int and repetitions > 0, "Repetitions must be positive")
    require(pilot or repetitions == 3, "Full run requires exactly three repetitions")
    require(not pilot or limitation.strip(), "Pilot needs an explicit limitation")
    cases = read(prompts)["cases"]
    case_lookup = {case["id"]: case for case in cases}
    require(len(case_lookup) == len(cases), "Duplicate prompt IDs")
    require(isinstance(responses, list) and responses, "Responses must be a nonempty JSON array")
    keys = set()
    replies = {}
    for record in responses:
        require(set(record) == {"case_id", "repetition", "condition", "response", "metadata"}, "Unexpected or missing response fields")
        require(record["case_id"] in case_lookup, "Unknown case ID")
        require(type(record["repetition"]) is int and 1 <= record["repetition"] <= repetitions, "Invalid repetition")
        require(record["condition"] in ("baseline", "skill"), "Invalid condition")
        require(isinstance(record["response"], str) and record["response"].strip(), "Empty response")
        require(json.dumps(record["metadata"], sort_keys=True, allow_nan=False) == json.dumps(metadata, sort_keys=True, allow_nan=False), "Conditions must use the verified identical generation metadata")
        key = (record["case_id"], record["repetition"], record["condition"])
        require(key not in keys, "Duplicate response")
        keys.add(key)
        replies[key] = record["response"]
    selected = sorted({key[0] for key in keys})
    require(pilot or set(selected) == set(case_lookup), "Full run requires every supplied prompt case")
    expected = {(case_id, repetition, condition) for case_id in selected for repetition in range(1, repetitions + 1) for condition in ("baseline", "skill")}
    require(keys == expected, "Missing or unbalanced case/repetition/condition records")
    rng = random.Random(seed if seed is not None else secrets.randbits(256))
    combinations = [(case_id, repetition) for case_id in selected for repetition in range(1, repetitions + 1)]
    rng.shuffle(combinations)
    first_conditions = ["baseline" if n % 2 == 0 else "skill" for n in range(len(combinations))]
    rng.shuffle(first_conditions)
    packets, mapping, template = [], {}, []
    for position, (case_id, repetition) in enumerate(combinations):
        opaque = f"pair-{position + 1:04d}"
        first = first_conditions[position]
        order = [first, "skill" if first == "baseline" else "baseline"]
        packets.append({"pair_id": opaque, "prompt": case_lookup[case_id]["prompt"], "replies": {label: replies[(case_id, repetition, condition)] for label, condition in zip(("A", "B"), order)}})
        mapping[opaque] = {"case_id": case_id, "repetition": repetition, "labels": dict(zip(("A", "B"), order))}
        template.append({"pair_id": opaque, "scores": {label: {"semantic_pass": None, "semantic_reason": "", "dimensions": {key: None for key in DIMENSIONS}} for label in ("A", "B")}, "preference": None, "reason": ""})
    output = Path(output)
    require(not output.exists(), "Output directory already exists; choose a fresh run")
    output.mkdir(parents=True)
    packet = {"instructions": "Assess each reply against the prompt. Semantic pass requires no invented decision-relevant facts, lost conditions, altered obligations, numbers or protected literals. Mark semantic pass/fail before clarity. Use null only for a clarity dimension that does not apply, and explain this in the preference reason. Prefer A, B or tie with a specific reason. A semantically failing reply cannot win; both failures require tie. Do not infer which condition produced a reply.", "dimensions": DIMENSIONS, "pairs": packets}
    write_new(output / "packets.json", packet)
    write_new(output / "judgments-template.json", template)
    write_new(output / "private-mapping.json", {"packet_sha256": digest(output / "packets.json"), "manifest": manifest, "pilot": pilot, "exploratory": exploratory, "unknown_generation_fields": unknown_fields({key: manifest[key] for key in ("model", "settings", "base_instructions_sha256")}, "generation"), "limitation": limitation if pilot else "Model judgment is an editorial proxy, not evidence of human comprehension.", "repetitions": repetitions, "mapping": mapping})
    return len(packets)


def validate_judgments(packet, judgments):
    require(isinstance(judgments, list), "Judgments must be an array")
    pair_ids = {pair["pair_id"] for pair in packet["pairs"]}
    require(len(pair_ids) == len(packet["pairs"]), "Duplicate packet IDs")
    seen = set()
    for row in judgments:
        require(set(row) == {"pair_id", "scores", "preference", "reason"}, "Unexpected judgment fields")
        require(row["pair_id"] in pair_ids and row["pair_id"] not in seen, "Unknown or duplicate judgment ID")
        seen.add(row["pair_id"])
        require(set(row["scores"]) == {"A", "B"}, "Both masked replies need scores")
        for score in row["scores"].values():
            require(set(score) == {"semantic_pass", "semantic_reason", "dimensions"}, "Unexpected score fields")
            require(type(score["semantic_pass"]) is bool, "Semantic pass/fail is required")
            require(isinstance(score["semantic_reason"], str) and score["semantic_reason"].strip(), "Semantic assessment needs a reason")
            require(set(score["dimensions"]) == set(DIMENSIONS), "Every clarity dimension must be assessed")
            require(all(value is None or (type(value) is int and value in (0, 1, 2)) for value in score["dimensions"].values()), "Dimensions require 0, 1, 2 or null")
        preference = row["preference"]
        require(preference in ("A", "B", "tie"), "Preference must be A, B or tie")
        require(isinstance(row["reason"], str) and row["reason"].strip(), "Preference needs a specific reason")
        if preference != "tie":
            require(row["scores"][preference]["semantic_pass"], "A semantically failing reply cannot win")
        a_pass, b_pass = (row["scores"][label]["semantic_pass"] for label in ("A", "B"))
        if a_pass != b_pass:
            require(preference == ("A" if a_pass else "B"), "The semantically passing reply must win over a failed reply")
    require(seen == pair_ids, "Judgments must cover every pair")


def lock_judgments(packet_path, judgments_path, output):
    validate_judgments(read(packet_path), read(judgments_path))
    write_new(output, {"packet_sha256": digest(packet_path), "judgments_sha256": digest(judgments_path)})


def score(packet_path, judgments_path, mapping_path, lock_path, output):
    packet, judgments, mapping, lock = map(read, (packet_path, judgments_path, mapping_path, lock_path))
    require(lock == {"packet_sha256": digest(packet_path), "judgments_sha256": digest(judgments_path)}, "Packet or judgments changed after locking")
    require(mapping["packet_sha256"] == digest(packet_path), "Mapping belongs to another packet")
    validate_judgments(packet, judgments)
    require(set(mapping["mapping"]) == {row["pair_id"] for row in judgments}, "Mapping must cover exactly the judged pairs")
    overall, by_case, by_repetition = Counter(), {}, {}
    failures = Counter()
    results = []
    identities = set()
    for row in judgments:
        identity = mapping["mapping"][row["pair_id"]]
        pair_identity = (identity["case_id"], identity["repetition"])
        require(pair_identity not in identities, "Duplicate private case/repetition mapping")
        identities.add(pair_identity)
        require(type(identity["repetition"]) is int and 1 <= identity["repetition"] <= mapping["repetitions"], "Invalid mapped repetition")
        labels = identity["labels"]
        require(set(labels) == {"A", "B"} and set(labels.values()) == {"baseline", "skill"}, "Invalid private condition mapping")
        outcome = "tie" if row["preference"] == "tie" else labels[row["preference"]]
        overall[outcome] += 1
        by_case.setdefault(identity["case_id"], Counter())[outcome] += 1
        by_repetition.setdefault(str(identity["repetition"]), Counter())[outcome] += 1
        passes = {labels[label]: value["semantic_pass"] for label, value in row["scores"].items()}
        for condition, passed in passes.items():
            if not passed:
                failures[condition] += 1
        regression = passes["baseline"] and not passes["skill"]
        overall["semantic_regressions"] += int(regression)
        by_case[identity["case_id"]]["semantic_regressions"] += int(regression)
        by_repetition[str(identity["repetition"])]["semantic_regressions"] += int(regression)
        results.append({**identity, "outcome": outcome, "semantic_regression": regression, "judgment": row})
    require(all(sum(counter[key] for key in ("skill", "baseline", "tie")) == mapping["repetitions"] for counter in by_case.values()), "Unbalanced private case mapping")
    def counts(counter):
        return {key: counter[key] for key in ("skill", "baseline", "tie")}
    case_results = {}
    for case_id, counter in sorted(by_case.items()):
        case_results[case_id] = {"replicate_outcomes": counts(counter), "semantic_regressions": counter["semantic_regressions"], "case_preference": "skill" if counter["skill"] > counter["baseline"] else "baseline" if counter["baseline"] > counter["skill"] else "tie"}
    limitations = [mapping["limitation"], "Repeated judgments from one model are not independent human readers; counts do not establish a comprehension gain.", "No confidence interval or significance claim is computed."]
    if mapping.get("exploratory", False):
        limitations.append("Exploratory pilot: model, sampling fields or complete base instructions may be unavailable; observed configuration parity does not establish an identical underlying model or independent generations. This is not a controlled comparison.")
    result = {"manifest": mapping["manifest"], "pilot": mapping["pilot"], "exploratory": mapping.get("exploratory", False), "unknown_generation_fields": mapping.get("unknown_generation_fields", []), "comparison_type": "exploratory editorial pilot" if mapping.get("exploratory", False) else "paired editorial assessment", "limitations": limitations, "pairs": len(judgments), "overall": counts(overall), "semantic_failures": {condition: failures[condition] for condition in ("baseline", "skill")}, "semantic_regressions": overall["semantic_regressions"], "by_case": case_results, "by_repetition": {key: {**counts(value), "semantic_regressions": value["semantic_regressions"]} for key, value in sorted(by_repetition.items())}, "unblinded_pairs": results}
    write_new(output, result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    prep = sub.add_parser("prepare", help="Validate raw paired replies and make masked packets")
    for name in ("responses", "manifest", "prompts", "skill", "output"):
        prep.add_argument(f"--{name}", required=True)
    prep.add_argument("--repetitions", type=int, default=3)
    prep.add_argument("--pilot", action="store_true")
    prep.add_argument("--exploratory", action="store_true", help="Pilot only: allow unavailable model/settings/base hash as null with observed host configuration")
    prep.add_argument("--limitation", default="")
    prep.add_argument("--seed", type=int, help="Reproducible shuffle; keep seed private")
    for command in ("lock", "score"):
        item = sub.add_parser(command)
        for name in ("packets", "judgments", "output"):
            item.add_argument(f"--{name}", required=True)
        if command == "score":
            item.add_argument("--mapping", required=True)
            item.add_argument("--lock", required=True)
    args = parser.parse_args()
    try:
        if args.command == "prepare":
            n = prepare(read(args.responses), read(args.manifest), args.prompts, args.skill, args.output, args.repetitions, args.pilot, args.limitation, args.seed, args.exploratory)
            if args.exploratory:
                print("Exploratory pilot: unavailable metadata recorded; this is not a controlled comparison.")
            print(f"Prepared {n} masked pairs. Keep private-mapping.json away from the assessor.")
        elif args.command == "lock":
            lock_judgments(args.packets, args.judgments, args.output)
            print("Judgments validated and locked. Unblinding is now allowed.")
        else:
            result = score(args.packets, args.judgments, args.mapping, args.lock, args.output)
            print(json.dumps({key: result[key] for key in ("pairs", "pilot", "exploratory", "comparison_type", "overall", "semantic_regressions")}))
    except (ValueError, KeyError, TypeError, OSError, json.JSONDecodeError) as error:
        parser.exit(2, f"error: {error}\n")


if __name__ == "__main__":
    main()
