"""Command line entry point: check an offline GoldenGate deployment export."""

from __future__ import annotations

import argparse
import sys

from .model import ExportError, load_export
from .rules import exit_code, run_all


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="gg-check",
        description="Offline posture check for OCI GoldenGate deployments (synthetic export).",
    )
    parser.add_argument("export", help="path to a JSON export of deployments")
    args = parser.parse_args(argv)
    try:
        deployments = load_export(args.export)
    except ExportError as exc:
        print(f"export error: {exc}", file=sys.stderr)
        return 3
    findings = run_all(deployments)
    prod = sum(1 for d in deployments if d.is_production())
    print(f"GoldenGate deployment check - {len(deployments)} deployment(s) "
          f"({prod} production), {len(findings)} finding(s)")
    for f in findings:
        print(f"[{f.severity:6}] {f.rule} deployment={f.target}")
        print(f"        {f.detail}")
    if findings:
        print(f"RESULT: {'HIGH findings present' if exit_code(findings) == 2 else 'medium/low findings only'}")
    else:
        print("RESULT: clean, no findings")
    return exit_code(findings)


if __name__ == "__main__":
    raise SystemExit(main())
