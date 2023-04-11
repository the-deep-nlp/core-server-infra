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

variable ecs_cluster_name {
    default = "nlp-server-cluster"
}

variable ecs_task_definition_name {
    default = "nlp-server-task"
}

variable ecs_service_name {
    default = "nlp-server-service"
}

variable ecs_container_name {
    default = "nlp-server-container"
}


# ecs role
variable ecs_task_execution_role {}
variable ecs_task_role {}

# alb
variable health_check_path {
    default = "/admin"
}

# route 53
variable domain_name {
    default = "labs.thedeep.io"
}

variable csrf_trusted_origins {
    default = "https://server.labs.thedeep.io"
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
    default = "*"
}
variable cron_create_indices_minute {
    default = 0
}
variable cron_create_indices_hour {
    default = "*"
}

# topicmodel
variable topicmodel_ecs_task_defn_arn {}
variable topicmodel_ecs_container_name {}

# Summarization
variable summarization_ecs_task_defn_arn {}
variable summarization_ecs_container_name {}

# NGrams
variable ngrams_ecs_task_defn_arn {}
variable ngrams_container_name {}

# Geolocations
variable geo_ecs_task_defn_arn {}
variable geo_ecs_container_name {}

# secrets
variable ssm_django_secret_key_arn {}
variable ssm_db_name_arn {}
variable ssm_db_username_arn {}
variable ssm_db_password_arn {}
variable ssm_db_port_arn {}
variable ssm_deep_db_name_arn {}
variable ssm_deep_db_username_arn {}
variable ssm_deep_db_password_arn {}
variable ssm_deep_db_port_arn {}
variable ssm_deep_db_host_arn {}
variable ssm_sentry_dsn_url_arn {}

# s3
variable nlp_server_bucket_static_name {}
variable nlp_server_bucket_static_arn {}
variable s3_bucketname_task_results_arn {}