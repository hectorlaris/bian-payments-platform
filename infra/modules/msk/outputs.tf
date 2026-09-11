output "cluster_arn" {
  description = "The MSK cluster ARN."
  value       = aws_msk_cluster.this.arn
}

output "bootstrap_brokers_tls" {
  description = "TLS bootstrap broker connection string."
  value       = aws_msk_cluster.this.bootstrap_brokers_tls
}

output "security_group_id" {
  description = "The MSK security group id."
  value       = aws_security_group.msk.id
}
