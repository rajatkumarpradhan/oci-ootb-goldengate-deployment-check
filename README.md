# oci-ootb-goldengate-deployment-check

**Category: built-in OCI services project (OOTB).** The custom portfolio project in this
pair is `oci-mysql-db-config-audit`.

## Which built-in OCI services this wires

- **OCI GoldenGate** (`oci_golden_gate_deployment`): the built-in managed replication
  service. Per the OCI provider docs a deployment records its environment type, OCPU
  count with optional **auto scaling**, a public or private endpoint (`is_public`), and
  an optional scheduled **backup schedule** to an Object Storage bucket. None of these
  choices is forced to the safer value at create time.

## Custom code vs native config

- **Native config**: `terraform/` declares one GoldenGate deployment with the
  review-friendly posture: production environment, auto scaling on, `is_public = false`,
  and a scheduled backup to Object Storage. Field names follow the oracle/oci provider
  docs (`oci_golden_gate_deployment`). **Template only - NOT plan/apply validated** (no
  live tenancy).
- **Custom code**: `gg_check/` audits an offline JSON export of deployments against four
  posture rules.

## The rules

| Rule | Severity | Fires when |
| ---- | -------- | ---------- |
| GGD001 | HIGH | A **production-environment** deployment records auto scaling **off** - throughput is capped at the base OCPU count through load peaks. |
| GGD002 | MEDIUM | A deployment records `is_public: true` - its console endpoint is reachable over the public internet; a private endpoint is the usual posture. Review flag. |
| GGD003 | MEDIUM | A **production-environment** deployment records **no backup schedule** in this export - a coverage gap as far as the export records; deployment backups are the documented recovery path. |
| GGD004 | LOW | No description and no tags recorded - hard to trace to an owner or purpose. |

Exit code: `2` on any HIGH, `1` on MEDIUM/LOW only, `0` when clean.

## Run it

```bash
python -m gg_check.cli samples/gg_messy.json   # exits 2, all 4 rules fire
python -m gg_check.cli samples/gg_clean.json   # exits 0
python -m unittest discover -s tests -v        # 22 tests, stdlib only
```

## Scope and sources

Only offline tests and synthetic demos ran locally and in GitHub Actions. Native
GoldenGate configuration is template-only and has **not** been plan/apply validated.
Findings describe what the supplied export records; they are review prompts, not proof
of effective exposure - a public endpoint can sit behind further network controls the
export does not model, and a missing schedule in the export does not prove none exists.
Field semantics follow the oracle/oci provider docs as of Nov 2026; verify current
behavior before acting. No live tenancy was touched.

- https://registry.terraform.io/providers/oracle/oci/latest/docs/resources/golden_gate_deployment

## Honest limits

- **Offline audit**: the JSON export is synthetic; nothing calls the OCI API.
- The environment label is read from the export; a deployment recorded with the wrong
  environment type is invisible to GGD001 and GGD003.
- No live tenancy was touched.

## Project status

Built as a daily OOTB project. 22 unit tests, green locally and in CI. Free tier only;
no live cloud calls, no spend.
