environment = "prod"
aws_region  = "us-east-1"
aws_profile = "nlp_tf"

# vpc
cidr_block         = "172.21.0.0/16"
availability_zones = ["us-east-1a", "us-east-1b"]

# ecs
app_image      = "nlp-server"
app_port       = 8000
fargate_cpu    = "2048"
fargate_memory = "4096"

# ecs role
ecs_task_execution_role = "ECSTaskExecutionNLPServerRole"
ecs_task_role           = "ECSTaskNLPServerRole"

# redis
redis_cluster_name    = "redis"
redis_node_type       = "cache.t2.micro"
redis_num_cache_nodes = 1
redis_port            = 6379

# ecs summarization
summarization_app_image_name = "summarization_model"
# ecs summarization v2
summarization_v2_app_image_name = "summarization_model_v2"
# ecs summarization v3
summarization_v3_app_image_name = "summarization_model_v3"
# ecs ngrams
ngrams_app_image_name = "ngrams_model"
# ecs topicmodel
topicmodel_app_image_name = "topicmodeling_model"
# ecs geolocations
geolocations_app_image_name = "geolocations_model"
# ecs text extraction
textextraction_app_image_name = "deepex_text_extraction"
# ecs entry extraction
entryextraction_app_image_name = "entry_extraction"

# s3
s3_bucketname_task_results = "nlp-tasks-processed-results"

# db table 
db_table_name             = "event_status_tracker"
db_table_callback_tracker = "failed_callback_tracker"

# ecs capacity
text_extraction_fargate_cpu = "2048"
text_extraction_fargate_memory = "4096"
summarization_v2_fargate_cpu = "2048"
summarization_v2_fargate_memory = "8192"
entry_extraction_fargate_cpu = "2048"
entry_extraction_fargate_memory = "4096"
geolocations_fargate_cpu = "512"
geolocations_fargate_memory = "2048"
ngrams_fargate_cpu = "512"
ngrams_fargate_memory = "1024"
topicmodeling_fargate_cpu = "1024"
topicmodeling_fargate_memory = "4096"

# model info
classification_model_id      = "classification_model"
classification_model_version = "1.0.0"
geolocation_model_id         = "geolocation_model"
geolocation_model_version    = "1.0.0"
reliability_model_id         = "reliability_model"
reliability_model_version    = "1.0.0"

ecr_image_reliability_name = "reliability"