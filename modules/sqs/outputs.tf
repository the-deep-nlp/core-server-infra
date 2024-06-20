output "queue_url" {
  value = aws_sqs_queue.text_extraction_connector_reqs.id
}