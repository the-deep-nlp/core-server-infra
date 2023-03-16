output ngrams_ecs_task_defn_arn {
    value = aws_ecs_task_definition.task-def.arn
}

output ngrams_container_name {
    value = var.ecs_container_name
}