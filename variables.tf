variable "environment" {}
variable "aws_region" {}
variable "aws_profile" {

}

# vpc
variable "cidr_block" {}

# ecs
variable "app_image" {}
variable "app_port" {}
variable "fargate_cpu" {}
variable "fargate_memory" {}

# ecs role
variable "ecs_task_execution_role" {}
variable "ecs_task_role" {}