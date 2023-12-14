output "private_dns_namespace_id" {
  value = aws_service_discovery_private_dns_namespace.item.id
}

output "private_dns_namespace_local_domain" {
  value = "${var.environment}-${var.local_domain}"
}