resource "aws_service_discovery_private_dns_namespace" "item" {
  name = "${var.environment}-${var.local_domain}"
  vpc  = var.vpc_id
}