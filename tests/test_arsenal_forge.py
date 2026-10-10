import unittest

from arsenal_forge.models import RepoProfile
from arsenal_forge.scanner import rank_repository_paths
from arsenal_forge.security import SecurityScanner
from arsenal_forge.compiler import render_skill_manifest


class ArsenalForgeTests(unittest.TestCase):
    def test_path_ranking_prefers_entry_points(self):
        paths = [
            "docs/guide.md",
            "src/deep/module.py",
            "src/main.py",
            "node_modules/pkg/index.js",
        ]
        ranked = rank_repository_paths(paths)
        self.assertEqual(ranked[0], "src/main.py")
        self.assertNotIn("node_modules/pkg/index.js", ranked)

    def test_security_gate_blocks_dynamic_exec(self):
        gate = SecurityScanner().gate({"tool.py": "value = eval(user_input)"})  # nosec AF003
        self.assertFalse(gate.passed)
        self.assertTrue(any(item.rule_id == "AF003" for item in gate.findings))

    def test_security_gate_allows_clean_text(self):
        gate = SecurityScanner().gate({"tool.py": "print('hello')"})
        self.assertTrue(gate.passed)
        self.assertEqual(gate.score, 100)

    def test_rule_scoped_nosec_suppression(self):
        source = "value = eval(user_input)  # nosec AF003"
        gate = SecurityScanner().gate({"tool.py": source})
        self.assertTrue(gate.passed)
        self.assertEqual(gate.score, 100)

    def test_manifest_defaults_to_unverified(self):
        profile = RepoProfile(
            owner="example",
            name="demo-skill",
            url="https://github.com/example/demo",
            language="Python",
            entry_points=["src/main.py"],
        )
        text = render_skill_manifest(profile)
        self.assertIn("verification: unverified", text)
        self.assertIn("https://github.com/example/demo", text)


if __name__ == "__main__":
    unittest.main()
