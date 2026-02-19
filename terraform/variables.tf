variable "project" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "us-central1"
}

variable "location" {
  description = "Resource location (for GCS + BigQuery)"
  type        = string
  default     = "US"
}

variable "bq_dataset_name" {
  description = "BigQuery dataset name"
  type        = string
  default     = "demo_dataset"
}

variable "gcs_bucket_name" {
  description = "Unique GCS bucket name"
  type        = string
}

variable "gcs_storage_class" {
  description = "GCS storage class"
  type        = string
  default     = "STANDARD"
}
