output "entryextraction_llm_ecs_task_defn_arn" {
  value = aws_ecs_task_definition.task-def.arn
}

output "entryextraction_llm_ecs_container_name" {
  value = var.ecs_container_name
}

output "application_endpoint" {
  value = "http://${aws_alb.alb.dns_name}:${var.app_port}"
}