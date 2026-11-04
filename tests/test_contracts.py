"""Structural contracts and real Git fixtures, not proof of model behavior."""
import re
from pathlib import Path
import tempfile
import unittest
import yaml

from fixtures import git, make_repo, source_snapshot

ROOT = Path(__file__).resolve().parents[1]
HOSTS = ('claude', 'codex', 'gemini', 'cursor', 'grok')
NAMES = {'eg-question', 'eg-brainstorm', 'eg-prd', 'eg-new-feature', 'eg-fix-bug', 'eg-precommit-review'}


def skill_path(host, name):
    if host in ('claude', 'gemini'):
        return ROOT / host / 'commands' / f'{name}.md'
    return ROOT / host / 'skills' / name / 'SKILL.md'


class Contracts(unittest.TestCase):
    def test_inventory_and_frontmatter(self):
        for host in HOSTS:
            files = list((ROOT / host / ('commands' if host in ('claude', 'gemini') else 'skills')).rglob('*.md'))
            self.assertEqual(len(files), 6)
            names = set()
            for path in files:
                with self.subTest(path=path):
                    text = path.read_text()
                    self.assertTrue(text.startswith('---\n'))
                    meta = yaml.safe_load(text.split('---', 2)[1])
                    self.assertIsInstance(meta['name'], str)
                    self.assertIsInstance(meta['description'], str)
                    self.assertIn(meta['name'], NAMES)
                    self.assertEqual(path, skill_path(host, meta['name']))
                    names.add(meta['name'])
                    if host in ('claude', 'cursor', 'grok'):
                        self.assertIs(meta['disable-model-invocation'], True)
                    self.assertNotIn('[BOOTSTRAP:', text)
                    self.assertNotIn('—', text)
            self.assertEqual(names, NAMES)

    def test_bootstrap_fetch_inventory_exists(self):
        for host in HOSTS:
            text = (ROOT / host / 'BOOTSTRAP.md').read_text()
            refs = re.findall(r'^- `([^`]+)`$', text, re.M)
            self.assertGreaterEqual(len(refs), 7)
            for ref in refs:
                self.assertTrue((ROOT / ref).is_file(), ref)
            for name in NAMES:
                self.assertIn(str(skill_path(host, name).relative_to(ROOT)), refs)
            self.assertNotIn('rm -rf', text)
            self.assertLess(text.index('## Fetch and validate first'), text.index('## Write only the reviewed result'))

    def test_codex_ui_manifests(self):
        for name in NAMES:
            data = yaml.safe_load((skill_path('codex', name).parent / 'agents/openai.yaml').read_text())
            self.assertIn('$' + name, data['interface']['default_prompt'])

    def test_cross_workflow_references(self):
        for host in HOSTS:
            for name in NAMES:
                refs = set(re.findall(r'\beg-(?:question|[a-z]+(?:-[a-z]+)+|prd|brainstorm)\b', skill_path(host, name).read_text()))
                self.assertLessEqual(refs, NAMES, (host, name, refs))

    def test_native_dispatch_does_not_leak_other_hosts(self):
        for name in NAMES:
            grok = skill_path('grok', name).read_text()
            self.assertIn('`task`', grok)
            self.assertNotIn('spawn_agent', grok)
            self.assertNotIn('fork_context', grok)
            self.assertNotIn('codex review', grok)
            self.assertNotIn('$eg-', grok)

    def test_reader_and_resume_contracts(self):
        for host in HOSTS:
            for name in NAMES:
                text = skill_path(host, name).read_text()
                self.assertIn('no parent conversation history', text)
                self.assertIn('Do not edit files, invoke workflows or', text)
                self.assertNotIn('locally as a separate cold prompt', text)
            for name in ('eg-new-feature', 'eg-precommit-review'):
                text = skill_path(host, name).read_text()
                self.assertIn('random UUID', text)
                self.assertIn('re-read this skill and the exact ledger', text)
            question = skill_path(host, 'eg-question').read_text()
            self.assertNotIn('## Recoverable run state', question)
            self.assertIn('never runs generators, tests', question)

    def test_readme_is_small_and_links_resolve(self):
        readme = (ROOT / 'README.md').read_text()
        self.assertLessEqual(len(readme.splitlines()), 100)
        for name in NAMES:
            self.assertIn(name, readme)
        for link in re.findall(r'\]\(([^)]+)\)', readme):
            if not link.startswith(('https://', '#')):
                self.assertTrue((ROOT / link).exists(), link)


class EvidenceFixtures(unittest.TestCase):
    def test_pending_layers_reveal_bug_hidden_by_combined_diff(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(tmp)
            before = source_snapshot(root)
            self.assertEqual(git(root, 'branch', '--show-current').strip(), b'trunk')
            self.assertEqual(git(root, 'diff', 'HEAD'), b'')
            staged = git(root, 'diff', '--cached')
            unstaged = git(root, 'diff')
            self.assertIn(b'+    return role != "admin"', staged)
            self.assertIn(b'-    return role != "admin"', unstaged)
            untracked = git(root, 'ls-files', '--others', '--exclude-standard', '-z')
            self.assertIn('currency ü.py'.encode(), untracked.split(b'\0'))
            self.assertEqual(source_snapshot(root), before)

    def test_untracked_content_change_needs_more_than_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_repo(tmp)
            status = git(root, 'status', '--porcelain=v1', '-z')
            before = source_snapshot(root)
            (root / 'currency ü.py').write_text('def cents(dollars):\n    return round(dollars * 100)\n')
            self.assertEqual(git(root, 'status', '--porcelain=v1', '-z'), status)
            self.assertNotEqual(source_snapshot(root), before)


if __name__ == '__main__':
    unittest.main()
