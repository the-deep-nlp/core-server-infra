variable environment {}
variable aws_region {}

# vpc
variable az_count {
    default = 2
}
variable availability_zones {
    default = ["us-east-1a", "us-east-1b"]
}
variable private_subnets {
    default = ["172.20.1.0/24", "172.20.2.0/24"]
}
variable public_subnets {
    default = ["172.20.10.0/24", "172.20.11.0/24"]
}
variable database_subnets {
    default = ["172.20.20.0/24", "172.20.21.0/24", "172.20.22.0/24"]
}
variable cidr_block {}

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
    default = 0
}
variable cron_deep_fetch_hour {
    default = "1"
}
variable cron_create_indices_minute {
    default = 0
}
variable cron_create_indices_hour {
    default = "1"
}