resource "aws_cloudwatch_log_group" "log_group" {
  name              = "/ecs/cloudflare-proxy-task-${var.environment}"
  retention_in_days = 30

  tags = {
    Name = "cw-log-group-cloudflare-proxy-${var.environment}"
  }
}

resource "aws_cloudwatch_log_stream" "log_stream" {
  name           = "log-stream-cloudflare-proxy-${var.environment}"
  log_group_name = aws_cloudwatch_log_group.log_group.name
}