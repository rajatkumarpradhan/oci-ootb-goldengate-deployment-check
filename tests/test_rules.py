import unittest

from gg_check.model import Deployment
from gg_check.rules import (
    exit_code,
    rule_no_identifiers,
    rule_prod_no_autoscaling,
    rule_prod_no_backup_schedule,
    rule_public_endpoint,
    run_all,
)


def dep(name="d", environment="production", auto_scaling=True, is_public=False,
        has_backup_schedule=True, description="x", tags=("team:a",)):
    return Deployment(name=name, environment=environment, auto_scaling=auto_scaling,
                      is_public=is_public, has_backup_schedule=has_backup_schedule,
                      description=description, tags=tuple(tags))


class TestGgd001(unittest.TestCase):
    def test_fires_prod_no_autoscaling(self):
        out = rule_prod_no_autoscaling((dep(auto_scaling=False),))
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0].severity, "HIGH")

    def test_quiet_dev_no_autoscaling(self):
        self.assertEqual(rule_prod_no_autoscaling((dep(environment="development", auto_scaling=False),)), [])

    def test_quiet_prod_autoscaling(self):
        self.assertEqual(rule_prod_no_autoscaling((dep(),)), [])


class TestGgd002(unittest.TestCase):
    def test_fires_public(self):
        out = rule_public_endpoint((dep(is_public=True),))
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0].severity, "MEDIUM")

    def test_quiet_private(self):
        self.assertEqual(rule_public_endpoint((dep(),)), [])


class TestGgd003(unittest.TestCase):
    def test_fires_prod_no_schedule(self):
        out = rule_prod_no_backup_schedule((dep(has_backup_schedule=False),))
        self.assertEqual(len(out), 1)

    def test_quiet_dev_no_schedule(self):
        self.assertEqual(rule_prod_no_backup_schedule((dep(environment="development", has_backup_schedule=False),)), [])


class TestGgd004(unittest.TestCase):
    def test_fires_no_identifiers(self):
        out = rule_no_identifiers((dep(description="", tags=()),))
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0].severity, "LOW")

    def test_quiet_with_description(self):
        self.assertEqual(rule_no_identifiers((dep(tags=()),)), [])


class TestAggregation(unittest.TestCase):
    def test_exit_2_on_high(self):
        self.assertEqual(exit_code(run_all((dep(auto_scaling=False),))), 2)

    def test_exit_1_medium_only(self):
        self.assertEqual(exit_code(run_all((dep(is_public=True),))), 1)

    def test_exit_0_clean(self):
        self.assertEqual(exit_code(run_all((dep(),))), 0)

    def test_sorted_high_first(self):
        out = run_all((dep(auto_scaling=False, is_public=True, description="", tags=()),))
        self.assertEqual(out[0].severity, "HIGH")
        self.assertEqual(out[-1].severity, "LOW")


if __name__ == "__main__":
    unittest.main()
