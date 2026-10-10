"""State restoration tests use real subprocesses and synthetic host events."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('builder', HERE.parent / 'scripts/build_plugin.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class HookTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        self.state = self.base / 'state'
        self.plugin = builder.build(HERE.parent, self.base / 'plugin', 'codex')
        self.command = [sys.executable, str(self.plugin / 'hooks/session_hook.py'),
                        '--host', 'codex', '--state-dir', str(self.state)]

    def tearDown(self):
        self.temp.cleanup()

    def event(self, name='SessionStart', sid='synthetic-session', **kwargs):
        payload = {'hook_event_name': name, 'session_id': sid, **kwargs}
        r = subprocess.run(self.command, input=json.dumps(payload), capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        if not r.stdout:
            return None
        result = json.loads(r.stdout)['hookSpecificOutput']
        self.assertEqual(result['hookEventName'], name)
        return result['additionalContext']

    def control(self, message, sid='synthetic-session'):
        return self.event('UserPromptSubmit', sid, prompt=message)

    def core(self):
        return (self.plugin / 'skills/palych/SKILL.md').read_text()

    def test_repeated_activation_sends_only_saved_acknowledgement(self):
        first = self.control('Enable palych.')
        self.assertTrue(first.endswith(self.core()))
        for prompt in ('Enable palych.', 'Включи palych всегда.'):
            repeated = self.control(prompt)
            self.assertNotIn(self.core(), repeated)
            metadata = json.loads(repeated.splitlines()[1])
            self.assertTrue(metadata['saved'])
            self.assertTrue(metadata['enabled'])
        self.assertIn('is ON', self.event(source='startup', sid='new'))

    def test_every_context_boundary_restores_full_core(self):
        self.control('Enable palych.')
        for source in ('startup', 'resume', 'clear', 'compact', 'fork'):
            context = self.event(source=source)
            self.assertTrue(context.endswith(self.core()))
            self.assertNotIn('saved', json.loads(context.splitlines()[1]))
            self.assertNotIn(self.core(), self.control('Enable palych.'))

    def test_changed_core_is_emitted_on_repeated_activation(self):
        self.control('Enable palych.')
        path = self.plugin / 'skills/palych/SKILL.md'
        path.write_text(self.core() + '\nSynthetic updated rule.\n')
        self.assertTrue(self.control('Enable palych.').endswith(self.core()))
        self.assertNotIn(self.core(), self.control('Enable palych.'))

    def test_reactivation_after_off_loads_full_core(self):
        self.control('Enable palych.')
        self.control('Turn off palych.')
        self.assertTrue(self.control('Enable palych.').endswith(self.core()))

    def test_helper_does_not_claim_emission(self):
        self.control('Enable palych.')
        for mode in ('off', 'on'):
            r = subprocess.run(self.command + ['set', '--session', 'synthetic-session',
                               '--mode', mode], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(self.control('Enable palych.').endswith(self.core()))

    def test_legacy_state_loads_then_deduplicates(self):
        import hashlib
        self.state.mkdir()
        key = hashlib.sha256(b'synthetic-session').hexdigest()
        (self.state / 'state.json').write_text(json.dumps({'always_on': False, 'sessions': {key: True}}))
        self.assertTrue(self.control('Enable palych.').endswith(self.core()))
        self.assertNotIn(self.core(), self.control('Enable palych.'))

    def test_missing_core_cannot_commit_activation_or_emission(self):
        path = self.plugin / 'skills/palych/SKILL.md'
        body = path.read_text()
        path.unlink()
        r = subprocess.run(self.command, input=json.dumps({'hook_event_name': 'UserPromptSubmit',
                           'session_id': 'synthetic-session', 'prompt': 'Enable palych.'}),
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 1)
        self.assertFalse((self.state / 'state.json').exists())
        path.write_text(body)
        self.assertTrue(self.control('Enable palych.').endswith(self.core()))

    def test_invalid_emission_marker_is_preserved(self):
        self.state.mkdir()
        path = self.state / 'state.json'
        original = json.dumps({'always_on': True, 'sessions': {}, 'emitted': {'invalid': 'invalid'}})
        path.write_text(original)
        r = subprocess.run(self.command, input=json.dumps({'hook_event_name': 'SessionStart',
                           'session_id': 'synthetic-session', 'source': 'compact'}),
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 1)
        self.assertEqual(path.read_text(), original)

    def test_metadata_argv_remains_executable_without_duplicate_values(self):
        context = self.control('Enable palych.')
        metadata = json.loads(context.splitlines()[1])
        argv = metadata['set_mode_argv']
        self.assertEqual(argv.count('synthetic-session'), 1)
        self.assertEqual(argv.count(str(self.state.resolve())), 1)
        argv[-1] = 'off'
        argv[0] = sys.executable
        r = subprocess.run(argv, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(json.loads(r.stdout), {'enabled': False, 'saved': True})
        self.assertIn('is OFF', self.event(source='compact'))

    def test_russian_display_name_controls(self):
        self.assertTrue(self.control('\u0412\u043a\u043b\u044e\u0447\u0438 \u041f\u0430\u043b\u044b\u0447\u0430.').endswith(self.core()))
        self.control('\u041e\u0442\u043a\u043b\u044e\u0447\u0438 \u041f\u0430\u043b\u044b\u0447\u0430.')
        self.assertIn('is OFF', self.event(source='compact'))
        self.control('\u0412\u043a\u043b\u044e\u0447\u0438 \u041f\u0430\u043b\u044b\u0447\u0430 \u0432\u0441\u0435\u0433\u0434\u0430.')
        self.assertIn('is ON', self.event(source='startup', sid='new'))
        self.control('\u041e\u0442\u043a\u043b\u044e\u0447\u0438 \u043f\u043e\u0441\u0442\u043e\u044f\u043d\u043d\u043e\u0435 \u0432\u043a\u043b\u044e\u0447\u0435\u043d\u0438\u0435 \u041f\u0430\u043b\u044b\u0447\u0430.')
        self.assertIn('is OFF', self.event(source='startup', sid='newer'))

    def test_old_name_is_not_a_new_namespace_control(self):
        self.assertIsNone(self.control('Enable clear-replies.'))
        self.assertFalse(self.state.exists())

    def test_install_is_off_and_does_not_write(self):
        context = self.event(source='startup')
        self.assertIn('is OFF', context)
        self.assertNotIn('## Preserve meaning', context)
        self.assertFalse(self.state.exists())

    def test_activate_then_restore_in_new_process_without_context(self):
        self.assertIn('## Preserve meaning', self.control('Включи palych для этого разговора.'))
        for source in ('compact', 'resume', 'clear', 'startup'):
            context = self.event(source=source)
            self.assertIn('is ON', context)
            self.assertTrue(context.endswith(self.core()))

    def test_off_overrides_global_after_compact(self):
        self.control('Enable palych always.')
        self.assertIn('is ON', self.event(source='startup', sid='another-session'))
        self.control('Turn off palych.')
        context = self.event(source='compact')
        self.assertIn('is OFF', context)
        self.assertNotIn('## Preserve meaning', context)
        self.assertIn('is ON', self.event(source='compact', sid='another-session'))

    def test_always_off_does_not_change_other_explicit_sessions(self):
        self.control('Enable palych.', sid='explicit')
        self.control('Enable palych always.')
        self.control('Disable palych always-on.')
        self.assertIn('is OFF', self.event(source='startup', sid='new'))
        self.assertIn('is ON', self.event(source='resume', sid='explicit'))

    def test_quoted_embedded_and_ordinary_prompts_are_not_controls(self):
        for prompt in ('«Отключи palych.»', 'Объясни фразу: Отключи palych.',
                       '```\nEnable palych always.\n```', 'What does HTTP 404 mean?'):
            self.assertIsNone(self.control(prompt))
        self.assertFalse(self.state.exists())

    def test_disable_and_reenable_with_other_language(self):
        self.control('Включи palych.')
        self.control('Turn off palych.')
        self.assertIn('is OFF', self.event(source='compact'))
        self.control('Enable palych.')
        self.assertIn('is ON', self.event(source='compact'))

    def test_arbitrary_session_id_cannot_escape_state_path(self):
        self.control('Enable palych.', sid='../../escape')
        saved = self.state / 'state.json'
        keys = list(json.loads(saved.read_text())['sessions'])
        self.assertEqual(len(keys), 1)
        self.assertEqual(len(keys[0]), 64)
        self.assertEqual(saved.stat().st_mode & 0o777, 0o600)
        self.assertNotIn('escape', saved.read_text())

    def test_malformed_state_is_reported_and_preserved(self):
        self.state.mkdir()
        config = self.state / 'state.json'
        config.write_text('{broken')
        r = subprocess.run(self.command, input=json.dumps({'hook_event_name': 'SessionStart',
                           'session_id': 's', 'source': 'compact'}), capture_output=True, text=True)
        self.assertEqual(r.returncode, 1)
        self.assertEqual(r.stdout, '')
        self.assertEqual(config.read_text(), '{broken')

    def test_natural_language_state_sync_helper(self):
        r = subprocess.run(self.command + ['set', '--session', 'synthetic-session', '--mode', 'on'],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(json.loads(r.stdout), {'enabled': True, 'saved': True})
        self.assertIn('is ON', self.event(source='compact'))

    def test_invalid_event_cannot_write(self):
        r = subprocess.run(self.command, input='{"hook_event_name":"UserPromptSubmit",'
                           '"prompt":"Enable palych.","session_id":null}',
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 1)
        self.assertFalse(self.state.exists())

    def test_subagent_and_unknown_events_do_not_mutate_parent(self):
        self.assertIsNone(self.event('UserPromptSubmit', prompt='Enable palych.', agent_id='worker'))
        self.assertIsNone(self.event('PostToolUse'))
        self.assertFalse(self.state.exists())

    def test_failed_commit_preserves_default_and_session_together(self):
        self.control('Enable palych.')
        original = (self.state / 'state.json').read_bytes()
        spec = importlib.util.spec_from_file_location('hook', self.plugin / 'hooks/session_hook.py')
        hook = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(hook)
        from unittest.mock import patch
        with patch.object(hook.os, 'replace', side_effect=OSError('simulated commit failure')):
            with self.assertRaises(OSError):
                hook.set_mode(self.state, 'synthetic-session', 'always-on')
        self.assertEqual((self.state / 'state.json').read_bytes(), original)
        self.assertIn('is OFF', self.event(source='startup', sid='another-session'))
        self.assertFalse(list(self.state.glob('.state-*')))

    def test_concurrent_sessions_do_not_lose_updates(self):
        jobs = [subprocess.Popen(self.command + ['set', '--session', f's{i}', '--mode', 'on'],
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                for i in range(8)]
        for job in jobs:
            _, err = job.communicate(timeout=10)
            self.assertEqual(job.returncode, 0, err)
        self.assertEqual(len(json.loads((self.state / 'state.json').read_text())['sessions']), 8)

    def test_builder_overwrite_guard_and_host_manifests(self):
        with self.assertRaisesRegex(ValueError, 'already exists'):
            builder.build(HERE.parent, self.plugin, 'codex')
        claude = builder.build(HERE.parent, self.base / 'claude', 'claude-code')
        self.assertTrue((claude / '.claude-plugin/plugin.json').is_file())
        self.assertTrue((self.plugin / '.codex-plugin/plugin.json').is_file())
        hooks = json.loads((self.plugin / 'hooks/hooks.json').read_text())
        self.assertIn('compact', hooks['hooks']['SessionStart'][0]['matcher'])
        self.assertIn('${PLUGIN_ROOT}', hooks['hooks']['SessionStart'][0]['hooks'][0]['command'])
        self.assertIn('${CLAUDE_PLUGIN_ROOT}', (claude / 'hooks/hooks.json').read_text())


if __name__ == '__main__':
    unittest.main()
