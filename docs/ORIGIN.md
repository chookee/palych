# Origin and naming

The project began as Clear Replies. Its standalone public name is
**Палыч / Palych**, chosen in honor of Anton Pavlovich Chekhov.

Palych 0.4.0 imports the prepared Clear Replies 0.3.0 source package and changes
its skill identifier, control commands, plugin names and local state namespace.
The conversational rules retain Russian priority, English support and exact
meaning. The package remains MIT licensed.

Historical synthetic evidence under evals/results and the original
observations/token counts is preserved byte-for-byte. Those records use the old
name and hashes. They measure earlier revisions, not Palych 0.4.0.
The new publication has independent Git history; the former workspace's history
and unrelated contents are not part of this repository.

The adapted plain-language source and exclusions are documented in
[references/sources.md](../skills/palych/references/sources.md). Reader comprehension and actual
host compaction have not been verified. Renaming does not establish either claim.

## Runtime state

New plugins use `~/.local/state/palych/<host>/`. Old Clear Replies state is neither
read nor modified. No global agent settings or installed skills are migrated by
this repository. Current control phrases are in [adapter docs](../adapters/README.md).
