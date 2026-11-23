import json
import os
import tempfile
import unittest

from gg_check.model import ExportError, load_export


def write(payload):
    fd, path = tempfile.mkstemp(suffix=".json")
    with os.fdopen(fd, "w") as fh:
        json.dump(payload, fh)
    return path


class TestLoad(unittest.TestCase):
    def test_load_ok(self):
        path = write({"deployments": [{"name": "a", "environment": "PRODUCTION"}]})
        (d,) = load_export(path)
        self.assertEqual(d.name, "a")
        self.assertTrue(d.is_production())

    def test_defaults(self):
        path = write({"deployments": [{"name": "a"}]})
        (d,) = load_export(path)
        self.assertEqual(d.environment, "development")
        self.assertTrue(d.auto_scaling)
        self.assertFalse(d.is_public)
        self.assertTrue(d.has_backup_schedule)
        self.assertFalse(d.is_production())

    def test_rejects_missing_name(self):
        with self.assertRaises(ExportError):
            load_export(write({"deployments": [{}]}))

    def test_rejects_bad_json(self):
        fd, path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(fd, "w") as fh:
            fh.write("{not json")
        with self.assertRaises(ExportError):
            load_export(path)

    def test_rejects_missing_key(self):
        with self.assertRaises(ExportError):
            load_export(write({"wrong": []}))

    def test_rejects_non_list(self):
        with self.assertRaises(ExportError):
            load_export(write({"deployments": {}}))


if __name__ == "__main__":
    unittest.main()
