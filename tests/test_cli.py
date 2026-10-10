import json
import tempfile
import unittest
from pathlib import Path

from arsenal_forge.cli import inspect_local


class CliTests(unittest.TestCase):
    def test_inspect_local_writes_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "demo"
            root.mkdir()
            (root / "main.py").write_text("print('hello')\n", encoding="utf-8")
            (root / "requirements.txt").write_text("", encoding="utf-8")

            out = Path(tmp) / "out"
            profile, gate = inspect_local(
                root=root,
                source_url="https://github.com/example/demo",
                name="demo",
                output_dir=out,
                language="Python",
            )

            self.assertTrue(gate.passed)
            self.assertEqual(profile.name, "demo")
            self.assertTrue((out / "SKILL.md").exists())
            self.assertTrue((out / "repo_profile.json").exists())
            self.assertTrue((out / "security_report.json").exists())

            payload = json.loads(
                (out / "security_report.json").read_text(encoding="utf-8")
            )
            self.assertEqual(payload["score"], 100)


if __name__ == "__main__":
    unittest.main()
