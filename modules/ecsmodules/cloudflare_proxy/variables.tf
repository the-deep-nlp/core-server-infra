variable "environment" {}
variable "aws_region" {}

variable "ecs_cluster_id" {}
variable "app_image_name" {}
variable "app_port" {
  default = "8191"
}
variable "fargate_cpu" {
  default = "512"
}
variable "fargate_memory" {
  default = "1024"
}

variable "app_count" {
  default = 1
}

variable "ecs_security_group_id" {}

# vpc
variable "vpc_id" {}
variable "public_subnets" {}
variable "private_subnets" {}

# iam
variable "iam_task_execution_role_arn" {}
variable "iam_ecs_task_arn" {}
variable "iam_ecs_task_execution_policy_arn" {}

# ecs
variable "ecs_task_definition_name" {
  default = "cloudflare-proxy-task"
}

variable "ecs_service_name" {
  default = "cloudflare-proxy-service"
}

variable "ecs_container_name" {
  default = "cloudflare-proxy-container"
}

variable "ecs_cluster_name" {
  default = "nlp-server-cluster"
}

variable "private_dns_namespace_id" {}
variable "private_dns_namespace_local_domain" {}

variable "local_sub_domain" {
  default = "cloudflare-proxy-srv"
}
