resource "aws_security_group" "allow_redis" {
  name        = "redis-sec-group-${var.environment}"
  description = "Allow Redis access from ECS"
  vpc_id      = var.vpc_id

  ingress {
    from_port       = var.redis_port
    to_port         = var.redis_port
    protocol        = "tcp"
    security_groups = [var.ecs_sec_grp_id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}