variable environment {}
variable aws_region {}

variable ecs_cluster_id {}
variable app_image {
    default = "nginx"
}
variable app_port {
    default = "8000"
}
variable fargate_cpu {
    default = "256"
}
variable fargate_memory {
    default = "512"
}

variable app_count {
    default = 1
}

variable ecs_security_group_id {}

# vpc
variable vpc_id {}
variable public_subnets {}
variable private_subnets {}

variable iam_task_execution_role_arn {}
variable iam_ecs_task_arn {}
variable iam_ecs_task_execution_policy_arn {}