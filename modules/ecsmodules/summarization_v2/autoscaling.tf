resource "aws_appautoscaling_target" "ecs_target" {
  max_capacity       = var.summarization_scaling_max_capacity
  min_capacity       = var.summarization_scaling_min_capacity
  resource_id        = "service/${var.ecs_cluster_id}/${var.ecs_service_name}-${var.environment}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
  role_arn           = aws_iam_role.ecs-autoscale-role.arn
  depends_on = [ aws_ecs_service.service ]
}

resource "aws_appautoscaling_policy" "ecs_target_cpu" {
  name               = "summarization-application-scaling-policy-cpu-${var.environment}"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.ecs_target.resource_id
  scalable_dimension = aws_appautoscaling_target.ecs_target.scalable_dimension
  service_namespace  = aws_appautoscaling_target.ecs_target.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    target_value = "${var.summarization_cpu_target_value}"
  }
  depends_on = [aws_appautoscaling_target.ecs_target]
}

resource "aws_appautoscaling_policy" "ecs_target_memory" {
  name               = "summarization-application-scaling-policy-memory-${var.environment}"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.ecs_target.resource_id
  scalable_dimension = aws_appautoscaling_target.ecs_target.scalable_dimension
  service_namespace  = aws_appautoscaling_target.ecs_target.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageMemoryUtilization"
    }
    target_value = "${var.summarization_mem_target_value}"
  }
  depends_on = [aws_appautoscaling_target.ecs_target]
}