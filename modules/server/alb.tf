
resource "aws_alb" "alb" {
  name           = "nlp-server-lb-${var.environment}"
  subnets        =  module.vpc.public_subnets
  security_groups = [aws_security_group.alb_sg.id]
}

resource "aws_alb_target_group" "tg" {
  name        = "alb-target-group-${var.environment}"
  port        = 80
  protocol    = "HTTP"
  target_type = "ip"
  vpc_id      = module.vpc.vpc_id

  health_check {
    port                = 80
    healthy_threshold   = 2
    unhealthy_threshold = 3
    timeout             = 30
    protocol            = "HTTP"
    matcher             = "200,301,302"
    path                = var.health_check_path
    interval            = 60
  }
}


# Redirecting all incomming traffic from ALB to the target group
resource "aws_alb_listener" "app_listener" {
  load_balancer_arn = aws_alb.alb.id
  port              = "443"
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-2016-08"
  certificate_arn   = aws_acm_certificate.acm_certificate.arn

  default_action {
    type             = "forward"
    target_group_arn = aws_alb_target_group.tg.arn
  }
}

data "aws_route53_zone" "zone" {
  name         = var.domain_name
  private_zone = false
}

# Add a record set in Route 53
resource "aws_route53_record" "terraform" {
  zone_id = "${data.aws_route53_zone.zone.zone_id}"
  name    = "server.${var.domain_name}"
  type    = "A"
  alias {
    name                   = "${aws_alb.alb.dns_name}"
    zone_id                = "${aws_alb.alb.zone_id}"
    evaluate_target_health = true
  }
} 