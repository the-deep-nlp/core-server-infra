variable "environment" {}
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
variable summarization_app_image_name {}

# ngrams ecs
variable ngrams_app_image_name {}

# topicmodel ecs
variable topicmodel_app_image_name {}

# geolocations ecs
variable geolocations_app_image_name {}

# db table
variable db_table_name {}
variable db_table_callback_tracker {}

# s3
variable s3_bucketname_task_results {}