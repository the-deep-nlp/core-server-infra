output "aws_service_discovery_service_endpoint" {
  value = "http://${var.local_sub_domain}-${var.environment}.${var.private_dns_namespace_local_domain}:${var.app_port}"
}