resource "aws_cloudwatch_log_group" "log_group" {
  name              = "/ecs/geolocations-task-${var.environment}"
  retention_in_days = 30

  tags = {
    Name = "cw-log-group-geolocations-${var.environment}"
  }
}

resource "aws_cloudwatch_log_stream" "log_stream" {
  name           = "log-stream-geolocations-${var.environment}"
  log_group_name = aws_cloudwatch_log_group.log_group.name
}