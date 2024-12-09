environment = "staging"
aws_region  = "us-east-1"
aws_profile = "nlp_tf"

# vpc
cidr_block         = "172.20.0.0/16"
availability_zones = ["us-east-1a", "us-east-1b"]

# ecs
app_image      = "nlp-server-staging"
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
summarization_app_image_name = "summarization_model_staging"
# ecs summarization v2
summarization_v2_app_image_name = "summarization_model_v2_staging"
# ecs summarization v3
summarization_v3_app_image_name = "summarization_model_v3_staging"
# ecs ngrams
ngrams_app_image_name = "ngrams_model_staging"
# ecs topicmodel
topicmodel_app_image_name = "topicmodeling_model_staging"
# ecs geolocations
geolocations_app_image_name = "geolocations_model_staging"
# ecs text extraction
textextraction_app_image_name = "deepex_text_extraction_staging"
# ecs entry extraction
entryextraction_app_image_name = "entry_extraction_staging"
# ecs entry extraction llm
entryextraction_llm_app_image_name = "entry_extraction_llm_staging"
# ecs cloudflare proxy server
cloudflare_proxy_srv_app_image_name = "flaresolver_staging"

# s3
s3_bucketname_task_results = "nlp-tasks-processed-results"

# db table 
db_table_name             = "event_status_tracker"
db_table_callback_tracker = "failed_callback_tracker"

# ecs capacity
text_extraction_fargate_cpu         = "2048"
text_extraction_fargate_memory      = "6144"
summarization_v2_fargate_cpu        = "2048"
summarization_v2_fargate_memory     = "8192"
summarization_v3_fargate_cpu        = "512"
summarization_v3_fargate_memory     = "1024"
entry_extraction_fargate_cpu        = "512"
entry_extraction_fargate_memory     = "2048"
geolocations_fargate_cpu            = "512"
geolocations_fargate_memory         = "2048"
ngrams_fargate_cpu                  = "512"
ngrams_fargate_memory               = "1024"
topicmodeling_fargate_cpu           = "1024"
topicmodeling_fargate_memory        = "4096"
cloudflare_proxy_srv_fargete_cpu    = "512"
cloudflare_proxy_srv_fargate_memory = "1024"

# ecs tasks count
text_extraction_task_count      = 1
entry_extraction_task_count     = 1
summarization_v3_task_count     = 1
geolocations_task_count         = 1
topicmodeling_task_count        = 1
cloudflare_proxy_srv_task_count = 1

# ecs tasks max and min
textextraction_scaling_max_capacity   = 5
textextraction_scaling_min_capacity   = 1
topicmodel_scaling_max_capacity       = 5
topicmodel_scaling_min_capacity       = 1
entryextraction_scaling_max_capacity  = 5
entryextraction_scaling_min_capacity  = 1
summarization_v3_scaling_max_capacity = 5
summarization_v3_scaling_min_capacity = 1

# model info
classification_model_id      = "classification_model"
classification_model_version = "1.0.0"
geolocation_model_id         = "geolocation_model"
geolocation_model_version    = "1.0.0"
reliability_model_id         = "reliability_model"
reliability_model_version    = "1.0.0"

ecr_image_reliability_name = "reliability"

# llm model selection
openai_main_model   = "gpt-4o"
openai_small_model  = "gpt-4o-mini"
bedrock_main_model  = "anthropic.claude-3-5-sonnet-20240620-v1:0"
bedrock_small_model = "us.amazon.nova-micro-v1:0"