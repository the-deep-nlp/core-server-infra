resource "aws_cloudwatch_log_group" "log_group" {
  name              = "/ecs/textextraction-task-${var.environment}"
  retention_in_days = 30

  tags = {
    Name = "cw-log-group-textextraction-${var.environment}"
  }
}

resource "aws_cloudwatch_log_stream" "log_stream" {
  name           = "log-stream-textextraction-${var.environment}"
  log_group_name = aws_cloudwatch_log_group.log_group.name
}