resource "aws_sqs_queue" "text_extraction_connector_reqs" {
  name = "te-connector-reqs-${var.environment}"
  delay_seconds = 0
  max_message_size = 262144
  message_retention_seconds = 86400
  receive_wait_time_seconds = 5
  visibility_timeout_seconds = 500

  tags = {
    Environment = var.environment
  }
}