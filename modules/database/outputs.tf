output "rds_instance_endpoint" {
  value = aws_rds_cluster.nlp_db.endpoint
}