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
    subnets          = module.vpc.private_subnets
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