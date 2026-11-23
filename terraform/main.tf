# TEMPLATE ONLY - NOT plan/apply validated against a live tenancy.
# Built-in resource: OCI GoldenGate deployment (oci_golden_gate_deployment).
# Field names per the oracle/oci provider docs. Posture shown: production
# environment, auto scaling on, private endpoint, scheduled backup to Object
# Storage.

terraform {
  required_providers {
    oci = {
      source  = "oracle/oci"
      version = ">= 5.0"
    }
  }
}

variable "compartment_ocid" {
  type        = string
  description = "OCID of the compartment that owns the deployment"
}

variable "subnet_ocid" {
  type        = string
  description = "OCID of the private subnet for the deployment endpoint"
}

variable "backup_bucket" {
  type        = string
  description = "Object Storage bucket that receives scheduled deployment backups"
}

resource "oci_golden_gate_deployment" "orders_replication" {
  compartment_id          = var.compartment_ocid
  display_name            = "orders-replication"
  deployment_type         = "OGG"
  environment_type        = "PRODUCTION"
  license_model           = "LICENSE_INCLUDED"
  cpu_core_count          = 2
  is_auto_scaling_enabled = true
  is_public               = false
  subnet_id               = var.subnet_ocid
  description             = "Orders database replication (production)"

  backup_schedule {
    bucket                    = var.backup_bucket
    compartment_id            = var.compartment_ocid
    frequency_backup_scheduled = "WEEKLY"
    is_metadata_only          = false
    time_backup_scheduled     = "2026-12-01T02:00:00Z"
  }

  freeform_tags = {
    "team" = "data"
    "env"  = "prod"
  }
}
