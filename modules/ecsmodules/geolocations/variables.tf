variable environment {}
variable aws_region {}

variable ecs_cluster_id {}
variable app_image_name {}
variable app_port {
    default = "80"
}
variable fargate_cpu {
    default = "4096"
}
variable fargate_memory {
    default = "20480"
}

variable app_count {
    default = 1
}

variable ecs_security_group_id {}

# vpc
variable vpc_id {}
variable public_subnets {}
variable private_subnets {}

# iam
variable iam_task_execution_role_arn {}
variable iam_ecs_task_arn {}
variable iam_ecs_task_execution_policy_arn {}

# ecs
variable ecs_task_definition_name {
    default = "geolocations-task"
}

variable ecs_service_name {
    default = "geolocations-service"
}

variable ecs_container_name {
    default = "geolocations-container"
}

variable efs_volume_id {}

# db
variable rds_instance_endpoint {}
variable ssm_db_name_arn {}
variable ssm_db_username_arn {}
variable ssm_db_password_arn {}
variable ssm_db_port_arn {}

# db table
variable db_table_name {}

# s3
variable s3_bucketname_task_results {}