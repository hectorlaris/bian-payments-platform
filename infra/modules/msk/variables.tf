variable "name_prefix" {
  description = "Prefix applied to resource names."
  type        = string
}

variable "vpc_id" {
  description = "VPC id where the cluster runs."
  type        = string
}

variable "vpc_cidr" {
  description = "VPC CIDR allowed to reach the brokers."
  type        = string
}

variable "subnet_ids" {
  description = "Subnets for the broker nodes (one per AZ)."
  type        = list(string)
}

variable "kafka_version" {
  description = "Apache Kafka version for MSK."
  type        = string
  default     = "3.6.0"
}

variable "broker_count" {
  description = "Number of broker nodes (multiple of subnet count)."
  type        = number
  default     = 2
}

variable "broker_instance_type" {
  description = "Broker instance type."
  type        = string
  default     = "kafka.t3.small"
}

variable "broker_volume_size" {
  description = "EBS volume size per broker in GiB."
  type        = number
  default     = 20
}

variable "tags" {
  description = "Common tags."
  type        = map(string)
  default     = {}
}
