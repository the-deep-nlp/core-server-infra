output "summarization_v2_ecs_task_defn_arn" {
  value = aws_ecs_task_definition.task-def.arn
}

output "summarization_v2_container_name" {
  value = var.ecs_container_name
}

output "aws_service_discovery_service_endpoint" {
  value = "http://${var.local_sub_domain}.${var.private_dns_namespace_local_domain}:${var.app_port}"
}