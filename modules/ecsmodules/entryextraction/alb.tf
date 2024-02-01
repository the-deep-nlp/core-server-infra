resource "aws_alb" "alb" {
  name            = "entry-ext-lb-${var.environment}"
  subnets         = var.public_subnets
  security_groups = [aws_security_group.alb_sg.id]
}

resource "aws_alb_target_group" "tg" {
  name        = "ent-ext-alb-target-grp-${var.environment}"
  port        = var.app_port
  protocol    = "HTTP"
  target_type = "ip"
  vpc_id      = var.vpc_id

  health_check {
    port                = var.app_port
    healthy_threshold   = 2
    unhealthy_threshold = 3
    timeout             = 30
    protocol            = "HTTP"
    matcher             = "200,301,302"
    path                = "/healthcheck"
    interval            = 60
  }
}


# Redirecting all incomming traffic from ALB to the target group
resource "aws_alb_listener" "app_listener" {
  load_balancer_arn = aws_alb.alb.id
  port              = var.app_port
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_alb_target_group.tg.arn
  }
}