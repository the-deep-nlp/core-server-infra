resource "aws_ecs_cluster" "cluster" {
  name = "${var.ecs_cluster_name}-${var.environment}"
}

data "aws_caller_identity" "current_user" {}

locals {
  app_image_url = "${data.aws_caller_identity.current_user.account_id}.dkr.ecr.${var.aws_region}.amazonaws.com/${var.app_image}:latest"
}

data "template_file" "config" {
  template = file("./modules/server/templates/ecr_image/image.json")

  vars = {
    app_image      = local.app_image_url
    app_port       = var.app_port
    fargate_cpu    = var.fargate_cpu
    fargate_memory = var.fargate_memory
    aws_region     = var.aws_region
    environment    = var.environment
    container_name = var.ecs_container_name

    # Django
    django_secret_key    = var.ssm_django_secret_key_arn
    debug                = "False"
    allowed_hosts        = "*"
    csrf_trusted_origins = var.environment == "prod" ? "https://server.${var.domain_name}" : "https://server-${var.environment}.${var.domain_name}"
    # Redis
    redis_host            = var.redis_host
    celery_broker_url     = var.redis_endpoint
    celery_result_backend = var.redis_endpoint
    # NLP Database
    nlp_db_name     = var.ssm_db_name_arn
    nlp_db_username = var.ssm_db_username_arn
    nlp_db_password = var.ssm_db_password_arn
    nlp_db_port     = var.ssm_db_port_arn
    nlp_db_host     = var.rds_instance_endpoint
    # DEEP Database
    deep_db_name     = var.ssm_deep_db_name_arn
    deep_db_username = var.ssm_deep_db_username_arn
    deep_db_password = var.ssm_deep_db_password_arn
    deep_db_port     = var.ssm_deep_db_port_arn
    deep_db_host     = var.ssm_deep_db_host_arn
    # Cron
    cron_deep_fetch_minute     = var.cron_deep_fetch_minute
    cron_deep_fetch_hour       = var.cron_deep_fetch_hour
    cron_create_indices_minute = var.cron_create_indices_minute
    cron_create_indices_hour   = var.cron_create_indices_hour
    # ECS
    ecs_cluster_name              = aws_ecs_cluster.cluster.id
    topicmodel_ecs_cluster_id     = aws_ecs_cluster.cluster.id
    topicmodel_ecs_task_defn_arn  = var.topicmodel_ecs_task_defn_arn
    topicmodel_ecs_container_name = var.topicmodel_ecs_container_name
    topicmodel_vpc_private_subnet = var.private_subnets[0]
    topicmodel_ecs_endpoint       = var.topicmodel_ecs_endpoint
    # ECS Summarization
    summarization_ecs_cluster_id     = aws_ecs_cluster.cluster.id
    summarization_ecs_task_defn_arn  = var.summarization_ecs_task_defn_arn
    summarization_ecs_container_name = var.summarization_ecs_container_name
    summarization_vpc_private_subnet = var.private_subnets[0]
    # ECS Summarization v2
    summarization_v2_ecs_cluster_id     = aws_ecs_cluster.cluster.id
    summarization_v2_ecs_task_defn_arn  = var.summarization_v2_ecs_task_defn_arn
    summarization_v2_ecs_container_name = var.summarization_v2_ecs_container_name
    summarization_v2_vpc_private_subnet = var.private_subnets[0]
    summarization_v2_ecs_endpoint       = var.summarization_v2_ecs_endpoint
    # ECS Summarization v3
    summarization_v3_ecs_cluster_id     = aws_ecs_cluster.cluster.id
    summarization_v3_ecs_task_defn_arn  = var.summarization_v3_ecs_task_defn_arn
    summarization_v3_ecs_container_name = var.summarization_v3_ecs_container_name
    summarization_v3_vpc_private_subnet = var.private_subnets[0]
    summarization_v3_ecs_endpoint       = var.summarization_v3_ecs_endpoint
    # ECS NGrams
    ngrams_ecs_cluster_id     = aws_ecs_cluster.cluster.id
    ngrams_ecs_task_defn_arn  = var.ngrams_ecs_task_defn_arn
    ngrams_ecs_container_name = var.ngrams_container_name
    ngrams_vpc_private_subnet = var.private_subnets[0]
    # ECS Geolocations
    geo_ecs_cluster_id     = aws_ecs_cluster.cluster.id
    geo_ecs_task_defn_arn  = var.geo_ecs_task_defn_arn
    geo_ecs_container_name = var.geo_ecs_container_name
    geo_vpc_private_subnet = var.private_subnets[0]
    geo_ecs_endpoint       = var.geo_ecs_endpoint
    # ECS Text Extraction
    # Text Extraction
    textextraction_ecs_cluster_id     = aws_ecs_cluster.cluster.id
    textextraction_ecs_task_defn_arn  = var.textextraction_ecs_task_defn_arn
    textextraction_ecs_container_name = var.textextraction_ecs_container_name
    textextraction_vpc_private_subnet = var.private_subnets[0]
    textextraction_ecs_endpoint       = var.textextraction_ecs_endpoint
    # Entry Extraction
    entryextraction_ecs_cluster_id     = aws_ecs_cluster.cluster.id
    entryextraction_ecs_task_defn_arn  = var.entryextraction_ecs_task_defn_arn
    entryextraction_ecs_container_name = var.entryextraction_ecs_container_name
    entryextraction_vpc_private_subnet = var.private_subnets[0]
    entryextraction_ecs_endpoint       = var.entryextraction_ecs_endpoint
    # Entry Extraction LLM
    entryextraction_llm_ecs_cluster_id     = aws_ecs_cluster.cluster.id
    entryextraction_llm_ecs_task_defn_arn  = var.entryextraction_llm_ecs_task_defn_arn
    entryextraction_llm_ecs_container_name = var.entryextraction_llm_ecs_container_name
    entryextraction_llm_vpc_private_subnet = var.private_subnets[0]
    entryextraction_llm_ecs_endpoint       = var.entryextraction_llm_ecs_endpoint
    # Sentry
    sentry_dsn_url = var.ssm_sentry_dsn_url_arn
    # s3
    nlp_server_bucket_static_name = var.nlp_server_bucket_static_name
    # Model info
    classification_model_id      = var.classification_model_id
    classification_model_version = var.classification_model_version
    geolocation_model_id         = var.geolocation_model_id
    geolocation_model_version    = var.geolocation_model_version
    reliability_model_id         = var.reliability_model_id
    reliability_model_version    = var.reliability_model_version
    # OpenAI API key
    ssm_openai_api_key_arn = var.ssm_openai_api_key_arn
  }
}

resource "aws_ecs_task_definition" "task-def" {
  family                   = "${var.ecs_task_definition_name}-${var.environment}"
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task.arn
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.fargate_cpu
  memory                   = var.fargate_memory
  container_definitions    = data.template_file.config.rendered
}

resource "aws_ecs_service" "service" {
  name                   = "${var.ecs_service_name}-${var.environment}"
  cluster                = aws_ecs_cluster.cluster.id
  task_definition        = aws_ecs_task_definition.task-def.arn
  desired_count          = var.app_count
  launch_type            = "FARGATE"
  enable_execute_command = true

  network_configuration {
    security_groups = [
      aws_security_group.ecs_sg.id
    ]
    subnets          = var.private_subnets
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = aws_alb_target_group.tg.arn
    container_name   = "${var.ecs_container_name}-${var.environment}"
    container_port   = var.app_port
  }

  depends_on = [
    aws_alb_listener.app_listener,
    aws_iam_role_policy_attachment.ecs_task_execution_role
  ]
}