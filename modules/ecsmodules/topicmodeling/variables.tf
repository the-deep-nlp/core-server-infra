variable "environment" {}
variable "aws_region" {}

variable "ecs_cluster_id" {}
variable "app_image_name" {}
variable "app_port" {
  default = "9000"
}
variable "fargate_cpu" {
  default = "1024"
}
variable "fargate_memory" {
  default = "4096"
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
  default = "topicmodel-task"
}

variable "ecs_service_name" {
  default = "topicmodel-service"
}

variable "ecs_container_name" {
  default = "topicmodel-container"
}

variable "ecs_cluster_name" {}

# db
variable "rds_instance_endpoint" {}
variable "ssm_db_name_arn" {}
variable "ssm_db_username_arn" {}
variable "ssm_db_password_arn" {}
variable "ssm_db_port_arn" {}
variable "ssm_sentry_dsn_url_arn" {}

# db table
variable "db_table_name" {}
variable "db_table_callback_tracker" {}

# s3
variable "s3_bucketname_task_results" {}

# autoscaling
variable "topicmodel_scaling_max_capacity" {
  default = 5
}

variable "topicmodel_scaling_min_capacity" {
  default = 1
}

variable "topicmodel_max_cpu_target_value" {
  default = 70
}

variable "topicmodel_min_cpu_target_value" {
  default = 60
}

variable "topicmodel_max_mem_target_value" {
  default = 60
}

variable "topicmodel_min_mem_target_value" {
  default = 50
}

variable "monitoring_period" {
  default = 30
}

variable "evaluation_period_max" {
  default = 3
}

variable "evaluation_period_min" {
  default = 8
}