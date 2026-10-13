"""Generated host packages follow the standalone skill and stay in sync with it."""
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
spec = importlib.util.spec_from_file_location('packages', ROOT / 'scripts/build_packages.py')
packages = importlib.util.module_from_spec(spec)
spec.loader.exec_module(packages)


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.files = packages.render(ROOT)

    def content(self, path):
        return self.files[path][0].decode('utf-8')

    def test_always_on_hosts_get_the_same_core(self):
        core = packages.load('install').payload(ROOT)
        self.assertEqual(self.content('packages/gemini/GEMINI.md'), core)
        rule = self.content('packages/cursor/rules/palych.mdc')
        self.assertTrue(rule.startswith('---\ndescription: '))
        self.assertIn('\nalwaysApply: true\n---\n\n', rule)
        self.assertTrue(rule.endswith(core))

    def test_catalogs_point_at_generated_packages(self):
        claude = json.loads(self.content('.claude-plugin/marketplace.json'))
        codex = json.loads(self.content('.agents/plugins/marketplace.json'))
        cursor = json.loads(self.content('.cursor-plugin/marketplace.json'))
        gemini = json.loads(self.content('gemini-extension.json'))
        sources = [claude['plugins'][0]['source'], codex['plugins'][0]['source']['path'],
                   cursor['plugins'][0]['source'], gemini['contextFileName']]
        for source in sources:
            relative = source.removeprefix('./')
            self.assertNotIn('..', relative)
            self.assertTrue(any(path == relative or path.startswith(relative + '/')
                                for path in self.files), source)

    def test_hermes_skill_has_no_links_outside_its_folder(self):
        skill = self.content('packages/hermes/palych/SKILL.md')
        self.assertNotIn('](adapters/', skill)
        self.assertIn('packages/hermes/palych/references/examples.ru.md', self.files)

    def test_drift_reports_changed_extra_and_missing_files(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for name in ('SKILL.md', 'LICENSE', 'references', 'adapters', 'scripts'):
                source = ROOT / name
                (shutil.copytree if source.is_dir() else shutil.copy2)(source, root / name)
            module_spec = importlib.util.spec_from_file_location('copy', root / 'scripts/build_packages.py')
            copy = importlib.util.module_from_spec(module_spec)
            module_spec.loader.exec_module(copy)
            copy.write(root)
            self.assertEqual(copy.drift(root), [])
            (root / 'packages/gemini/GEMINI.md').write_text('edited\n', encoding='utf-8')
            (root / 'packages/extra.txt').write_text('stale\n', encoding='utf-8')
            (root / 'gemini-extension.json').unlink()
            problems = '\n'.join(copy.drift(root))
            self.assertIn('packages/gemini/GEMINI.md: differs', problems)
            self.assertIn('packages/extra.txt: not produced', problems)
            self.assertIn('gemini-extension.json: missing', problems)


if __name__ == '__main__':
    unittest.main()
