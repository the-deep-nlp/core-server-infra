data "aws_caller_identity" "current_user" {}

locals {
  app_image_url = "${data.aws_caller_identity.current_user.account_id}.dkr.ecr.${var.aws_region}.amazonaws.com/${var.app_image_name}:latest"
}

resource "aws_ecs_task_definition" "task-def" {
  family                   = "${var.ecs_task_definition_name}-${var.environment}"
  execution_role_arn       = var.iam_task_execution_role_arn
  task_role_arn            = var.iam_ecs_task_arn
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.fargate_cpu
  memory                   = var.fargate_memory
  container_definitions    = <<DEFINITION
[
  {
      "memory": ${var.fargate_memory},
      "cpu": ${var.fargate_cpu},
      "networkMode": "awsvpc",
      "logConfiguration": {
          "logDriver": "awslogs",
          "options": {
            "awslogs-group": "/ecs/entryextraction-task-${var.environment}",
            "awslogs-region": "${var.aws_region}",
            "awslogs-stream-prefix": "ecs"
          }
      },
      "portMappings": [
        {
          "containerPort": ${var.app_port},
          "hostPort": ${var.app_port}
        }
      ],
      "essential": true,
      "command": [
        "uvicorn", "app:ecs_app", "--host", "0.0.0.0", "--port", "${var.app_port}"
      ],
      "name": "${var.ecs_container_name}-${var.environment}",
      "image": "${local.app_image_url}",
      "environment": [
        {
          "name": "DB_HOST",
          "value": "${var.rds_instance_endpoint}"
        },
        {
          "name": "DB_TABLE_NAME",
          "value": "${var.db_table_name}"
        },
        {
          "name": "DB_TABLE_CALLBACK_TRACKER",
          "value": "${var.db_table_callback_tracker}"
        },
        {
          "name": "S3_BUCKET_NAME",
          "value": "${var.s3_bucketname_task_results}"
        },
        {
          "name": "ENVIRONMENT",
          "value": "${var.environment}"
        },
        {
          "name": "GEOLOCATION_ECS_ENDPOINT",
          "value": "${var.geo_ecs_endpoint}"
        },
        {
          "name": "REDIS_HOST",
          "value": "${var.redis_host}"       
        },
        {
          "name": "OPENAI_MAIN_MODEL",
          "value": "${var.openai_main_model}"       
        },
        {
          "name": "OPENAI_SMALL_MODEL",
          "value": "${var.openai_small_model}"       
        },
        {
          "name": "BEDROCK_MAIN_MODEL",
          "value": "${var.bedrock_main_model}"       
        },
        {
          "name": "BEDROCK_SMALL_MODEL",
          "value": "${var.bedrock_small_model}"       
        }
      ],
      "secrets": [
        {
          "name": "DB_NAME",
          "valueFrom": "${var.ssm_db_name_arn}"
        },
        {
          "name": "DB_USER",
          "valueFrom": "${var.ssm_db_username_arn}"
        },
        {
          "name": "DB_PWD",
          "valueFrom": "${var.ssm_db_password_arn}"
        },
        {
          "name": "DB_PORT",
          "valueFrom": "${var.ssm_db_port_arn}"
        },
        {
          "name": "DEEP_DB_NAME",
          "valueFrom": "${var.ssm_deep_db_name_arn}"
        },
        {
          "name": "DEEP_DB_USER",
          "valueFrom": "${var.ssm_deep_db_username_arn}"
        },
        {
          "name": "DEEP_DB_PASSWORD",
          "valueFrom": "${var.ssm_deep_db_password_arn}"
        },
        {
          "name": "DEEP_DB_PORT",
          "valueFrom": "${var.ssm_deep_db_port_arn}"
        },
        {
          "name": "DEEP_DB_HOST",
          "valueFrom": "${var.ssm_deep_db_host_arn}"
        },
        {
          "name": "SENTRY_DSN",
          "valueFrom": "${var.ssm_sentry_dsn_url_arn}"
        },
        {
          "name": "OPENAI_API_KEY",
          "valueFrom": "${var.ssm_openai_api_key_arn}"
        }
      ]
  }
]
DEFINITION
}

resource "aws_ecs_service" "service" {
  name            = "${var.ecs_service_name}-${var.environment}"
  cluster         = var.ecs_cluster_id
  task_definition = aws_ecs_task_definition.task-def.arn
  desired_count   = var.app_count
  launch_type     = "FARGATE"

  network_configuration {
    security_groups = [
      var.ecs_security_group_id
    ]
    subnets          = var.private_subnets
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_alb_target_group.tg.arn
    container_name   = "${var.ecs_container_name}-${var.environment}"
    container_port   = var.app_port
  }

  depends_on = [
    aws_alb_listener.app_listener,
    var.iam_ecs_task_execution_policy_arn
  ]
}
