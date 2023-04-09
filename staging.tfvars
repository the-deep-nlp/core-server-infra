environment = "staging"
aws_region  = "us-east-1"
aws_profile = "nlp_tf"

# vpc
cidr_block = "172.20.0.0/16"
availability_zones = ["us-east-1a", "us-east-1b"]

# ecs
app_image      = "testserver" #nlp-server"
app_port       = 8000
fargate_cpu    = "256" #"2048"
fargate_memory = "512" #"4096"

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
# ecs ngrams
ngrams_app_image_name = "ngrams_model"
# ecs topicmodel
topicmodel_app_image_name = "topicmodeling_model"
# ecs geolocations
geolocations_app_image_name = "geolocations_model"

# s3
s3_bucketname_task_results = "test-ecs-parser11"

# db table 
db_table_name = "event_status_tracker"