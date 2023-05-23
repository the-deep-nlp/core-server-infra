variable "environment" {}

variable "nlp_server_static_bucket" {
  type    = string
  default = "nlp-server-static"
}

variable "s3_bucketname_task_results" {}

variable "nlp_docs_conversion_bucket" {
  type = string
  default = "nlp-docs-conversion"
}