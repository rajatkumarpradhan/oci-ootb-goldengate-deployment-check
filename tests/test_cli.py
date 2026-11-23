import json
import os
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO

from gg_check.cli import main


def write(payload):
    fd, path = tempfile.mkstemp(suffix=".json")
    with os.fdopen(fd, "w") as fh:
        json.dump(payload, fh)
    return path


CLEAN = {"deployments": [{"name": "ok", "environment": "production", "auto_scaling": True,
                          "is_public": False, "has_backup_schedule": True,
                          "description": "orders replication", "tags": ["team:data"]}]}
MESSY = {"deployments": [{"name": "bad", "environment": "production", "auto_scaling": False,
                          "is_public": True, "has_backup_schedule": False}]}


class TestCli(unittest.TestCase):
    def run_cli(self, payload):
        path = write(payload)
        out, err = StringIO(), StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = main([path])
        return code, out.getvalue(), err.getvalue()

    def test_clean_exit_0(self):
        code, out, _ = self.run_cli(CLEAN)
        self.assertEqual(code, 0)
        self.assertIn("no findings", out)

    def test_messy_exit_2(self):
        code, out, _ = self.run_cli(MESSY)
        self.assertEqual(code, 2)
        for rule in ("GGD001", "GGD002", "GGD003", "GGD004"):
            self.assertIn(rule, out)

    def test_export_error_exit_3(self):
        code, _, err = self.run_cli({"wrong": []})
        self.assertEqual(code, 3)
        self.assertIn("export error", err)


if __name__ == "__main__":
    unittest.main()
