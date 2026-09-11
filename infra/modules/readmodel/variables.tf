variable "name_prefix" {
  description = "Prefix applied to resource names."
  type        = string
}

variable "point_in_time_recovery" {
  description = "Enable DynamoDB point-in-time recovery."
  type        = bool
  default     = true
}

variable "tags" {
  description = "Common tags."
  type        = map(string)
  default     = {}
}
