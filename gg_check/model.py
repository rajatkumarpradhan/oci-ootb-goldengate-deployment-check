"""Data model and export loading for the GoldenGate deployment check."""

from __future__ import annotations

import json
from dataclasses import dataclass


class ExportError(ValueError):
    """Raised when an export file is malformed."""


PROD_ENVIRONMENTS = ("prod", "production")


@dataclass(frozen=True)
class Deployment:
    name: str
    environment: str = "development"
    auto_scaling: bool = True
    is_public: bool = False
    has_backup_schedule: bool = True
    description: str = ""
    tags: tuple = ()

    def is_production(self) -> bool:
        return any(c in self.environment.lower() for c in PROD_ENVIRONMENTS)


def load_export(path: str) -> tuple:
    with open(path, "r", encoding="utf-8") as fh:
        try:
            raw = json.load(fh)
        except json.JSONDecodeError as exc:
            raise ExportError(f"{path}: not valid JSON: {exc}") from exc
    if not isinstance(raw, dict) or "deployments" not in raw:
        raise ExportError(f"{path}: top level must hold a 'deployments' list")
    if not isinstance(raw["deployments"], list):
        raise ExportError(f"{path}: 'deployments' must be a list")
    deployments = []
    for i, d in enumerate(raw["deployments"]):
        where = f"deployments[{i}]"
        if not isinstance(d, dict):
            raise ExportError(f"{where}: must be an object")
        if "name" not in d:
            raise ExportError(f"{where}: missing required field 'name'")
        deployments.append(Deployment(
            name=d["name"],
            environment=str(d.get("environment", "development")),
            auto_scaling=bool(d.get("auto_scaling", True)),
            is_public=bool(d.get("is_public", False)),
            has_backup_schedule=bool(d.get("has_backup_schedule", True)),
            description=str(d.get("description", "")),
            tags=tuple(d.get("tags", [])),
        ))
    return tuple(deployments)
