variable "aws_region" {
  description = "AWS region"
  default     = "ap-south-1"
}

variable "ami_id" {
  description = "Ubuntu 22.04 LTS AMI"
  default     = "ami-087d1c9a513324697" # Update for your region
}

variable "master_instance_type" {
  description = "Master node instance type"
  default     = "t3.large"
}

variable "worker_instance_type" {
  description = "Worker node instance type"
  default     = "t3.medium"
}

variable "worker_count" {
  description = "Number of worker nodes"
  default     = 2
}

variable "key_name" {
  description = "SSH key pair name"
  type        = string
  default = "kubekey"
}
