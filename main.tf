terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "4.8.0"
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
  aws_region = var.aws_region
  
  # vpc
  cidr_block = var.cidr_block
  availability_zones = var.availability_zones
}

module "nlp_database" {
  source = "./modules/database"

  environment = var.environment

  # vpc
  vpc_id           = module.nlp_vpc.aws_vpc_id
  database_subnets = module.nlp_vpc.public_subnets
  availability_zones = var.availability_zones
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
  redis_host = module.redis.redis_host
  # vpc
  vpc_id = module.nlp_vpc.aws_vpc_id
  private_subnets = module.nlp_vpc.private_subnets
  public_subnets = module.nlp_vpc.public_subnets
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