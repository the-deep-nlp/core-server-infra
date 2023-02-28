variable "environment" {}
variable "aws_region" {}
variable "aws_profile" {

}

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

# ecr
variable "ngrams_ecr_image_url" {}

# summarization ecs
variable summarization_app_image_name {}