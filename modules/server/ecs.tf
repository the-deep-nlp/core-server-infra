resource "aws_ecs_cluster" "cluster" {
  name = "nlp-server-backend-${var.environment}"
}

data "template_file" "config" {
  template = file("./modules/server/templates/ecr_image/image.json")

  vars = {
    app_image      = var.app_image #"${data.aws_ssm_parameter.ecr_backend_image_url.value}:latest"
    app_port       = var.app_port
    fargate_cpu    = var.fargate_cpu
    fargate_memory = var.fargate_memory
    aws_region     = var.aws_region
    environment    = var.environment

    # Django
    django_secret_key = data.aws_ssm_parameter.django_secret_key.arn
    debug = "False"
    allowed_hosts = "*"
    # Redis
    redis_host = var.redis_host #data.aws_ssm_parameter.celery_redis_url.arn
    celery_broker_url = var.redis_endpoint
    celery_result_backend = var.redis_endpoint
    # NLP Database
    nlp_db_name = data.aws_ssm_parameter.db_name.arn
    nlp_db_username = data.aws_ssm_parameter.db_username.arn
    nlp_db_password = data.aws_ssm_parameter.db_password.arn
    nlp_db_port = data.aws_ssm_parameter.db_port.arn
    nlp_db_host = var.rds_instance_endpoint
    # DEEP Database
    deep_db_name = data.aws_ssm_parameter.deep_db_name.arn
    deep_db_username = data.aws_ssm_parameter.deep_db_username.arn
    deep_db_password = data.aws_ssm_parameter.deep_db_password.arn
    deep_db_port = data.aws_ssm_parameter.deep_db_port.arn
    deep_db_host = data.aws_ssm_parameter.deep_db_host.arn
    # Cron
    cron_deep_fetch_minute = var.cron_deep_fetch_minute
    cron_deep_fetch_hour = var.cron_deep_fetch_hour
    cron_create_indices_minute = var.cron_create_indices_minute
    cron_create_indices_hour = var.cron_create_indices_hour
  }
}

resource "aws_ecs_task_definition" "task-def" {
  family                   = "backend-server-task-${var.environment}"
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task.arn
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.fargate_cpu
  memory                   = var.fargate_memory
  container_definitions    = data.template_file.config.rendered
}

resource "aws_ecs_service" "service" {
  name            = "backend-server-service-${var.environment}"
  cluster         = aws_ecs_cluster.cluster.id
  task_definition = aws_ecs_task_definition.task-def.arn
  desired_count   = var.app_count
  launch_type     = "FARGATE"

  network_configuration {
    security_groups  = [
        aws_security_group.ecs_sg.id
    ]
    subnets          = aws_subnet.private.*.id
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = aws_alb_target_group.tg.arn
    container_name   = "backend-server-${var.environment}"
    container_port   = var.app_port
  }

  depends_on = [
    aws_alb_listener.app_listener,
    aws_iam_role_policy_attachment.ecs_task_execution_role
  ]
}