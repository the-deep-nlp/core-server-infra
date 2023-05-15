terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 4.44.0"
    }
  }
  required_version = "1.1.2"
  backend "s3" {
    bucket = "terraform-state-deep"
    key    = "nlp_core_server/terraform.tfstate"
    region = "us-east-1"
    #   dynamodb_table  = "terraform-lock-integration-db"
    encrypt = true
    profile = "nlp_tf"
  }
}

provider "aws" {
  region  = var.aws_region
  profile = var.aws_profile
  #shared_credentials_files = ["~/.aws/credentials"]
}

module "nlp_vpc" {
  source = "./modules/vpc"

  environment = var.environment
  aws_region  = var.aws_region

  # vpc
  cidr_block         = var.cidr_block
  availability_zones = var.availability_zones
}

module "nlp_database" {
  source = "./modules/database"

  environment = var.environment

  # vpc
  vpc_id             = module.nlp_vpc.aws_vpc_id
  database_subnets   = module.nlp_vpc.public_subnets
  availability_zones = var.availability_zones

  # secrets
  ssm_db_name_value     = module.secrets.ssm_db_name_value
  ssm_db_username_value = module.secrets.ssm_db_username_value
  ssm_db_password_value = module.secrets.ssm_db_password_value
  ssm_db_port_value     = module.secrets.ssm_db_port_value
}

module "nlp_server" {
  source = "./modules/server"

  environment = var.environment
  aws_region  = var.aws_region

  # ecs
  app_image      = var.app_image
  app_port       = var.app_port
  fargate_cpu    = var.fargate_cpu
  fargate_memory = var.fargate_memory
  # ecs role
  ecs_task_execution_role = var.ecs_task_execution_role
  ecs_task_role           = var.ecs_task_role
  # nlp database
  rds_instance_endpoint = module.nlp_database.rds_instance_endpoint
  # redis endpoint
  redis_endpoint = module.redis.redis_endpoint
  redis_host     = module.redis.redis_host
  # vpc
  vpc_id          = module.nlp_vpc.aws_vpc_id
  private_subnets = module.nlp_vpc.private_subnets
  public_subnets  = module.nlp_vpc.public_subnets

  # secrets
  ssm_django_secret_key_arn = module.secrets.ssm_django_secret_key_arn
  ssm_db_name_arn           = module.secrets.ssm_db_name_arn
  ssm_db_username_arn       = module.secrets.ssm_db_username_arn
  ssm_db_password_arn       = module.secrets.ssm_db_password_arn
  ssm_db_port_arn           = module.secrets.ssm_db_port_arn
  ssm_deep_db_name_arn      = module.secrets.ssm_deep_db_name_arn
  ssm_deep_db_username_arn  = module.secrets.ssm_deep_db_username_arn
  ssm_deep_db_password_arn  = module.secrets.ssm_deep_db_password_arn
  ssm_deep_db_port_arn      = module.secrets.ssm_deep_db_port_arn
  ssm_deep_db_host_arn      = module.secrets.ssm_deep_db_host_arn
  ssm_sentry_dsn_url_arn    = module.secrets.ssm_sentry_dsn_url_arn

  # Topic Modeling
  topicmodel_ecs_task_defn_arn  = module.topicmodel.topicmodel_ecs_task_defn_arn
  topicmodel_ecs_container_name = module.topicmodel.topicmodel_container_name

  # Summarization
  summarization_ecs_task_defn_arn  = module.summarization.s_ecs_task_defn_arn
  summarization_ecs_container_name = module.summarization.s_ecs_container_name

  # Summarization v2
  summarization_v2_ecs_task_defn_arn = module.summarization_v2.summarization_v2_ecs_task_defn_arn
  summarization_v2_ecs_container_name = module.summarization_v2.summarization_v2_container_name
  summarization_v2_ecs_endpoint = module.summarization_v2.aws_service_discovery_service_endpoint

  # NGrams
  ngrams_ecs_task_defn_arn = module.ngrams.ngrams_ecs_task_defn_arn
  ngrams_container_name    = module.ngrams.ngrams_container_name

  # Geolocations
  geo_ecs_task_defn_arn  = module.geolocations.geo_ecs_task_defn_arn
  geo_ecs_container_name = module.geolocations.geo_ecs_container_name

  # s3
  nlp_server_bucket_static_name  = module.s3.nlp_server_bucket_static_name
  nlp_server_bucket_static_arn   = module.s3.nlp_server_bucket_static_arn
  s3_bucketname_task_results_arn = module.s3.task_results_bucket_arn
}

module "redis" {
  source = "./modules/redis"

  environment = var.environment

  # redis
  redis_cluster_name    = var.redis_cluster_name
  redis_node_type       = var.redis_node_type
  redis_num_cache_nodes = var.redis_num_cache_nodes
  redis_port            = var.redis_port

  # vpc
  vpc_id          = module.nlp_vpc.aws_vpc_id
  private_subnets = module.nlp_vpc.private_subnets

  # sec grp
  ecs_sec_grp_id = module.nlp_server.ecs_sec_grp_id
}

module "secrets" {
  source = "./modules/secrets"
}

module "topicmodel" {
  source = "./modules/ecsmodules/topicmodeling"

  environment = var.environment
  aws_region  = var.aws_region

  # ecs
  ecs_cluster_id = module.nlp_server.ecs_cluster_id

  # security grp
  ecs_security_group_id = module.nlp_server.ecs_security_group_id

  # vpc
  vpc_id          = module.nlp_vpc.aws_vpc_id
  private_subnets = module.nlp_vpc.private_subnets
  public_subnets  = module.nlp_vpc.public_subnets

  iam_task_execution_role_arn       = module.nlp_server.iam_task_execution_role_arn
  iam_ecs_task_arn                  = module.nlp_server.iam_ecs_task_arn
  iam_ecs_task_execution_policy_arn = module.nlp_server.iam_ecs_task_execution_policy_arn

  # ecr
  app_image_name = var.topicmodel_app_image_name

  # secrets
  rds_instance_endpoint  = module.nlp_database.rds_instance_endpoint
  ssm_db_name_arn        = module.secrets.ssm_db_name_arn
  ssm_db_username_arn    = module.secrets.ssm_db_username_arn
  ssm_db_password_arn    = module.secrets.ssm_db_password_arn
  ssm_db_port_arn        = module.secrets.ssm_db_port_arn
  ssm_sentry_dsn_url_arn = module.secrets.ssm_sentry_dsn_url_arn

  # db table
  db_table_name             = var.db_table_name
  db_table_callback_tracker = var.db_table_callback_tracker

  # s3
  s3_bucketname_task_results = module.s3.task_results_bucket_name
}

module "ngrams" {
  source = "./modules/ecsmodules/ngrams"

  environment = var.environment
  aws_region  = var.aws_region

  # ecs
  ecs_cluster_id = module.nlp_server.ecs_cluster_id

  # security grp
  ecs_security_group_id = module.nlp_server.ecs_security_group_id

  # vpc
  vpc_id          = module.nlp_vpc.aws_vpc_id
  private_subnets = module.nlp_vpc.private_subnets
  public_subnets  = module.nlp_vpc.public_subnets

  iam_task_execution_role_arn       = module.nlp_server.iam_task_execution_role_arn
  iam_ecs_task_arn                  = module.nlp_server.iam_ecs_task_arn
  iam_ecs_task_execution_policy_arn = module.nlp_server.iam_ecs_task_execution_policy_arn

  # ecr
  app_image_name = var.ngrams_app_image_name

  # secrets
  rds_instance_endpoint  = module.nlp_database.rds_instance_endpoint
  ssm_db_name_arn        = module.secrets.ssm_db_name_arn
  ssm_db_username_arn    = module.secrets.ssm_db_username_arn
  ssm_db_password_arn    = module.secrets.ssm_db_password_arn
  ssm_db_port_arn        = module.secrets.ssm_db_port_arn
  ssm_sentry_dsn_url_arn = module.secrets.ssm_sentry_dsn_url_arn

  # db table
  db_table_name             = var.db_table_name
  db_table_callback_tracker = var.db_table_callback_tracker

  # s3
  s3_bucketname_task_results = module.s3.task_results_bucket_name
}

module "summarization" {
  source = "./modules/ecsmodules/summarization"

  environment = var.environment
  aws_region  = var.aws_region

  # ecs
  ecs_cluster_id = module.nlp_server.ecs_cluster_id

  # security grp
  ecs_security_group_id = module.nlp_server.ecs_security_group_id

  # vpc
  vpc_id          = module.nlp_vpc.aws_vpc_id
  private_subnets = module.nlp_vpc.private_subnets
  public_subnets  = module.nlp_vpc.public_subnets

  iam_task_execution_role_arn       = module.nlp_server.iam_task_execution_role_arn
  iam_ecs_task_arn                  = module.nlp_server.iam_ecs_task_arn
  iam_ecs_task_execution_policy_arn = module.nlp_server.iam_ecs_task_execution_policy_arn

  # efs
  efs_volume_id = module.efilesystem.efs_volume_id

  # ecr
  app_image_name = var.summarization_app_image_name

  # secrets
  rds_instance_endpoint  = module.nlp_database.rds_instance_endpoint
  ssm_db_name_arn        = module.secrets.ssm_db_name_arn
  ssm_db_username_arn    = module.secrets.ssm_db_username_arn
  ssm_db_password_arn    = module.secrets.ssm_db_password_arn
  ssm_db_port_arn        = module.secrets.ssm_db_port_arn
  ssm_sentry_dsn_url_arn = module.secrets.ssm_sentry_dsn_url_arn

  # db table
  db_table_name             = var.db_table_name
  db_table_callback_tracker = var.db_table_callback_tracker

  # s3
  s3_bucketname_task_results = module.s3.task_results_bucket_name
}

module "geolocations" {
  source = "./modules/ecsmodules/geolocations"

  environment = var.environment
  aws_region  = var.aws_region

  # ecs
  ecs_cluster_id = module.nlp_server.ecs_cluster_id

  # security grp
  ecs_security_group_id = module.nlp_server.ecs_security_group_id

  # vpc
  vpc_id          = module.nlp_vpc.aws_vpc_id
  private_subnets = module.nlp_vpc.private_subnets
  public_subnets  = module.nlp_vpc.public_subnets

  iam_task_execution_role_arn       = module.nlp_server.iam_task_execution_role_arn
  iam_ecs_task_arn                  = module.nlp_server.iam_ecs_task_arn
  iam_ecs_task_execution_policy_arn = module.nlp_server.iam_ecs_task_execution_policy_arn

  # efs
  efs_volume_id = module.efilesystem.efs_volume_id

  # ecr
  app_image_name = var.geolocations_app_image_name

  # secrets
  rds_instance_endpoint    = module.nlp_database.rds_instance_endpoint
  ssm_db_name_arn          = module.secrets.ssm_db_name_arn
  ssm_db_username_arn      = module.secrets.ssm_db_username_arn
  ssm_db_password_arn      = module.secrets.ssm_db_password_arn
  ssm_db_port_arn          = module.secrets.ssm_db_port_arn
  ssm_sentry_dsn_url_arn   = module.secrets.ssm_sentry_dsn_url_arn
  ssm_geoname_api_user_arn = module.secrets.ssm_geoname_api_user_arn

  # db table
  db_table_name             = var.db_table_name
  db_table_callback_tracker = var.db_table_callback_tracker

  # s3
  s3_bucketname_task_results = module.s3.task_results_bucket_name
}

module "efilesystem" {
  source = "./modules/efs"

  environment = var.environment
  aws_region  = var.aws_region

  # vpc
  vpc_id                  = module.nlp_vpc.aws_vpc_id
  availability_zone_count = 2 #module.nlp_vpc.availability_zone_count
  private_subnets         = module.nlp_vpc.private_subnets
}

module "s3" {
  source = "./modules/s3"

  environment                = var.environment
  s3_bucketname_task_results = var.s3_bucketname_task_results
}

module "summarization_v2" {
  source = "./modules/ecsmodules/summarization_v2"

  environment = var.environment
  aws_region  = var.aws_region

  # ecs
  ecs_cluster_id = module.nlp_server.ecs_cluster_id

  # security grp
  ecs_security_group_id = module.nlp_server.ecs_security_group_id

  # vpc
  vpc_id          = module.nlp_vpc.aws_vpc_id
  private_subnets = module.nlp_vpc.private_subnets
  public_subnets  = module.nlp_vpc.public_subnets

  iam_task_execution_role_arn       = module.nlp_server.iam_task_execution_role_arn
  iam_ecs_task_arn                  = module.nlp_server.iam_ecs_task_arn
  iam_ecs_task_execution_policy_arn = module.nlp_server.iam_ecs_task_execution_policy_arn

  # ecr
  app_image_name = var.summarization_v2_app_image_name

  # secrets
  rds_instance_endpoint  = module.nlp_database.rds_instance_endpoint
  ssm_db_name_arn        = module.secrets.ssm_db_name_arn
  ssm_db_username_arn    = module.secrets.ssm_db_username_arn
  ssm_db_password_arn    = module.secrets.ssm_db_password_arn
  ssm_db_port_arn        = module.secrets.ssm_db_port_arn
  ssm_sentry_dsn_url_arn = module.secrets.ssm_sentry_dsn_url_arn

  # db table
  db_table_name             = var.db_table_name
  db_table_callback_tracker = var.db_table_callback_tracker

  # s3
  s3_bucketname_task_results = module.s3.task_results_bucket_name
  # efs
  efs_volume_id = module.efilesystem.efs_volume_id

  # cloudmap
  private_dns_namespace_id = module.cloudmap.private_dns_namespace_id
  private_dns_namespace_local_domain = module.cloudmap.private_dns_namespace_local_domain
}

module "cloudmap" {
  source = "./modules/cloudmap"
  environment = var.environment
  # vpc
  vpc_id = module.nlp_vpc.aws_vpc_id
}