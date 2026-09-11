variable "name_prefix" {
  description = "Prefix applied to resource names."
  type        = string
}

variable "log_retention_days" {
  description = "Retention for the notification log group."
  type        = number
  default     = 14
}

variable "tags" {
  description = "Common tags."
  type        = map(string)
  default     = {}
}
