variable environment {}
variable aws_region {}

# vpc
variable vpc_id {}
variable public_subnets {}
variable private_subnets {}

# ecs
variable app_image {}
variable app_port {}
variable fargate_cpu {}
variable fargate_memory {}
variable app_count {
    default = 1
}

# ecs role
variable ecs_task_execution_role {}
variable ecs_task_role {}

# alb
variable health_check_path {
    default = "/admin/"
}

# route 53
variable domain_name {
    default = "labs.thedeep.io"
}

# database
variable rds_instance_endpoint {}

# redis
variable redis_endpoint {}
variable redis_host {}

# cron
variable cron_deep_fetch_minute {
    default = "*/5"
}
variable cron_deep_fetch_hour {
    default = "*"
}
variable cron_create_indices_minute {
    default = 0
}
variable cron_create_indices_hour {
    default = "*"
}