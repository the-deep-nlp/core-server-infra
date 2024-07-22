output "aws_service_discovery_service_host" {
  value = "${var.local_sub_domain}-${var.environment}.${var.private_dns_namespace_local_domain}"
}