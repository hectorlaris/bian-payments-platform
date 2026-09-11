output "cluster_arn" {
  description = "The ECS cluster ARN."
  value       = aws_ecs_cluster.this.arn
}

output "task_execution_role_arn" {
  description = "The ECS task execution role ARN."
  value       = aws_iam_role.task_execution.arn
}

output "log_group_name" {
  description = "The service log group name."
  value       = aws_cloudwatch_log_group.services.name
}
