environment = "staging"
aws_region  = "us-east-1"
aws_profile = "nlp_tf"

# vpc
cidr_block = "172.20.0.0/16"
availability_zones = ["us-east-1a", "us-east-1b"]

# ecs
app_image      = "testserver" #"961104659532.dkr.ecr.us-east-1.amazonaws.com/nlp-server:latest"
app_port       = 80
fargate_cpu    = "256"
fargate_memory = "512"

# ecs role
ecs_task_execution_role = "ECSTaskExecutionNLPServerRole"
ecs_task_role           = "ECSTaskNLPServerRole"

# redis
redis_cluster_name    = "redis"
redis_node_type       = "cache.t2.micro"
redis_num_cache_nodes = 1
redis_port            = 6379

# ecr
ngrams_ecr_image_url = "961104659532.dkr.ecr.us-east-1.amazonaws.com/lambda-ngrams:latest"

# ecs summarization
summarization_app_image_name = "summarization_model"