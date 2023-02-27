data "template_file" "config" {
  template = file("./modules/ecsmodules/ngrams/templates/ecr_image/image.json")

  vars = {
    app_image      = var.app_image #"${data.aws_ssm_parameter.ecr_backend_image_url.value}:latest"
    app_port       = var.app_port
    fargate_cpu    = var.fargate_cpu
    fargate_memory = var.fargate_memory
    aws_region     = var.aws_region
    environment    = var.environment
  }
}

resource "aws_ecs_task_definition" "task-def" {
  family                   = "ngrams-task-${var.environment}"
  execution_role_arn       = var.iam_task_execution_role_arn
  task_role_arn            = var.iam_ecs_task_arn
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.fargate_cpu
  memory                   = var.fargate_memory
  container_definitions    = data.template_file.config.rendered
}

resource "aws_ecs_service" "service" {
  name            = "ngrams-service-${var.environment}"
  cluster         = var.ecs_cluster_id
  task_definition = aws_ecs_task_definition.task-def.arn
  desired_count   = var.app_count
  launch_type     = "FARGATE"

  network_configuration {
    security_groups  = [
        var.ecs_security_group_id
    ]
    subnets          = var.private_subnets
    assign_public_ip = false
  }

#   load_balancer {
#     target_group_arn = aws_alb_target_group.tg.arn
#     container_name   = "backend-server-${var.environment}"
#     container_port   = var.app_port
#   }

  depends_on = [
    #aws_alb_listener.app_listener,
    var.iam_ecs_task_execution_policy_arn
  ]
}