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
            "awslogs-group": "/ecs/cloudflare-proxy-task-${var.environment}",
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
      "name": "${var.ecs_container_name}-${var.environment}",
      "image": "${local.app_image_url}"
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

  depends_on = [
    var.iam_ecs_task_execution_policy_arn
  ]
  service_registries {
    registry_arn = aws_service_discovery_service.subdomain.arn
  }
}

resource "aws_service_discovery_service" "subdomain" {
  name = "${var.local_sub_domain}-${var.environment}"
  dns_config {
    namespace_id = var.private_dns_namespace_id
    dns_records {
      ttl  = 10
      type = "A"
    }
    routing_policy = "MULTIVALUE"
  }
}