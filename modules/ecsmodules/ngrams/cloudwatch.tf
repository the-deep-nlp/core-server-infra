resource "aws_cloudwatch_log_group" "log_group" {
  name              = "/ecs/ngrams-task-${var.environment}"
  retention_in_days = 30

  tags = {
    Name = "cw-log-group-ngrams-${var.environment}"
  }
}

resource "aws_cloudwatch_log_stream" "log_stream" {
  name           = "log-stream-ngrams-${var.environment}"
  log_group_name = aws_cloudwatch_log_group.log_group.name
}