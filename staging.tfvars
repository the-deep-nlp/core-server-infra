environment = "staging"
aws_region  = "us-east-1"
aws_profile = "nlp_tf"

# vpc
cidr_block = "172.20.0.0/16"

# ecs
app_image      = "nginx:latest"
app_port       = 80
fargate_cpu    = "256"
fargate_memory = "512"

# ecs role
ecs_task_execution_role = "ECSTaskExecutionNLPServerRole"
ecs_task_role           = "ECSTaskNLPServerRole"