output "nlp_server_bucket_static_name" {
  value = aws_s3_bucket.static.id
}

output "nlp_server_bucket_static_arn" {
  value = aws_s3_bucket.static.arn
}

output "task_results_bucket_name" {
  value = aws_s3_bucket.processed_bucket.id
}

output "task_results_bucket_arn" {
  value = aws_s3_bucket.processed_bucket.arn
}

output "nlp_docs_conversion_bucket_name" {
  value = aws_s3_bucket.docs_conversion.id
}

output "nlp_docs_conversion_bucket_arn" {
  value = aws_s3_bucket.docs_conversion.arn
}