variable "environment" {
  type        = string
  description = "Deployment environment"
  validation {
    condition     = contains(["staging", "prod"], var.environment)
    error_message = "Valid value is one of the following: staging, prod."
  }
}
variable "aws_region" {}
variable "aws_profile" {}

# vpc
variable "cidr_block" {}
variable "availability_zones" {}

# ecs
variable "app_image" {}
variable "app_port" {}
variable "fargate_cpu" {}
variable "fargate_memory" {}

# ecs role
variable "ecs_task_execution_role" {}
variable "ecs_task_role" {}

# redis
variable "redis_cluster_name" {}
variable "redis_node_type" {}
variable "redis_num_cache_nodes" {}
variable "redis_port" {}

# summarization ecs
variable "summarization_app_image_name" {}

# summarization v2 ecs
variable "summarization_v2_app_image_name" {}

# summarization v3 ecs
variable "summarization_v3_app_image_name" {}

# ngrams ecs
variable "ngrams_app_image_name" {}

# topicmodel ecs
variable "topicmodel_app_image_name" {}

# geolocations ecs
variable "geolocations_app_image_name" {}

# text extraction ecs
variable "textextraction_app_image_name" {}

# entry extraction ecs
variable "entryextraction_app_image_name" {}

# entry extraction llm ecs
variable "entryextraction_llm_app_image_name" {}

# cloudflare proxy server
variable "cloudflare_proxy_srv_app_image_name" {}

# db table
variable "db_table_name" {}
variable "db_table_callback_tracker" {}

# s3
variable "s3_bucketname_task_results" {}

# Model info
variable "classification_model_id" {}
variable "classification_model_version" {}
variable "geolocation_model_id" {}
variable "geolocation_model_version" {}
variable "reliability_model_id" {}
variable "reliability_model_version" {}

# reliability ecr image name
variable "ecr_image_reliability_name" {}

# ecs capacity
variable "text_extraction_fargate_cpu" {}
variable "text_extraction_fargate_memory" {}
variable "summarization_v2_fargate_cpu" {}
variable "summarization_v2_fargate_memory" {}
variable "summarization_v3_fargate_cpu" {}
variable "summarization_v3_fargate_memory" {}
variable "entry_extraction_fargate_cpu" {}
variable "entry_extraction_fargate_memory" {}
variable "geolocations_fargate_cpu" {}
variable "geolocations_fargate_memory" {}
variable "ngrams_fargate_cpu" {}
variable "ngrams_fargate_memory" {}
variable "topicmodeling_fargate_cpu" {}
variable "topicmodeling_fargate_memory" {}
variable "cloudflare_proxy_srv_fargete_cpu" {}
variable "cloudflare_proxy_srv_fargate_memory" {}

# ecs task count
variable "text_extraction_task_count" {}
variable "entry_extraction_task_count" {}
variable "summarization_v3_task_count" {}
variable "geolocations_task_count" {}
variable "topicmodeling_task_count" {}
variable "cloudflare_proxy_srv_task_count" {}

# ecs task max and min
variable "textextraction_scaling_max_capacity" {}
variable "textextraction_scaling_min_capacity" {}
variable "topicmodel_scaling_max_capacity" {}
variable "topicmodel_scaling_min_capacity" {}
variable "entryextraction_scaling_max_capacity" {}
variable "entryextraction_scaling_min_capacity" {}
variable "summarization_v3_scaling_max_capacity" {}
variable "summarization_v3_scaling_min_capacity" {}