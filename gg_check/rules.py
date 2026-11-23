"""GGD001-GGD004 rules."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Finding:
    rule: str
    severity: str  # HIGH | MEDIUM | LOW
    target: str
    detail: str


def rule_prod_no_autoscaling(deployments: tuple) -> list:
    """GGD001 HIGH: production-environment deployment with auto scaling off."""
    return [
        Finding("GGD001", "HIGH", d.name,
                "production-environment deployment records auto scaling off; throughput is capped "
                "at the base OCPU count through load peaks. Review flag")
        for d in deployments if d.is_production() and not d.auto_scaling
    ]


def rule_public_endpoint(deployments: tuple) -> list:
    """GGD002 MEDIUM: deployment with a public endpoint."""
    return [
        Finding("GGD002", "MEDIUM", d.name,
                "deployment records is_public true; its console endpoint is reachable over the "
                "public internet - a private endpoint is the usual posture. Review flag")
        for d in deployments if d.is_public
    ]


def rule_prod_no_backup_schedule(deployments: tuple) -> list:
    """GGD003 MEDIUM: production deployment with no backup schedule recorded."""
    return [
        Finding("GGD003", "MEDIUM", d.name,
                "production-environment deployment records no backup schedule in this export; "
                "a coverage gap as far as the export records, not proof none exists - deployment "
                "backups are the documented recovery path. Review flag")
        for d in deployments if d.is_production() and not d.has_backup_schedule
    ]


def rule_no_identifiers(deployments: tuple) -> list:
    """GGD004 LOW: no description and no tags recorded."""
    return [
        Finding("GGD004", "LOW", d.name,
                "no description and no tags recorded; hard to trace to an owner or purpose")
        for d in deployments if not d.description and not d.tags
    ]


ALL_RULES = (
    rule_prod_no_autoscaling,
    rule_public_endpoint,
    rule_prod_no_backup_schedule,
    rule_no_identifiers,
)

_SEVERITY_RANK = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}


def run_all(deployments: tuple) -> list:
    findings = []
    for rule in ALL_RULES:
        findings.extend(rule(deployments))
    findings.sort(key=lambda x: (_SEVERITY_RANK[x.severity], x.rule, x.target))
    return findings


def exit_code(findings: list) -> int:
    if any(f.severity == "HIGH" for f in findings):
        return 2
    if findings:
        return 1
    return 0
