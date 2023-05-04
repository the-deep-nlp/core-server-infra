output topicmodel_ecs_task_defn_arn {
    value = aws_ecs_task_definition.task-def.arn
}

output topicmodel_container_name {
    value = var.ecs_container_name
}