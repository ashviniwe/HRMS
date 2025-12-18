variable "aws_region" {
  description = "AWS region"
  default     = "ap-southeast-1"
}

variable "ami_id" {
  description = "Ubuntu 22.04 LTS AMI"
  default     = "ami-00d8fc944fb171e29" # Update for your region
}

variable "master_instance_type" {
  description = "Master node instance type"
  default     = "t3.large"
}

variable "worker_instance_type" {
  description = "Worker node instance type"
  default     = "c6a.xlarge"
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

# CIDRs allowed to access HTTP/HTTPS NodePorts (e.g., 30080, 30443)
variable "allowed_http_nodeports_cidrs" {
  description = "List of CIDR blocks allowed to reach HTTP/S NodePorts on worker nodes"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

# CIDRs allowed to access Istio ingress gateway health port 15021
variable "allowed_istio_health_cidrs" {
  description = "List of CIDR blocks allowed to reach Istio health check port 15021 on worker nodes"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

# HTTP/S NodePorts commonly used by Istio ingressgateway
variable "http_nodeports" {
  description = "HTTP/S NodePort values to explicitly open on worker nodes"
  type        = list(number)
  default     = [30080, 30443]
}

# Toggle to provision an AWS NLB in front of Istio ingressgateway
variable "enable_nlb" {
  description = "Whether to provision a Network Load Balancer targeting worker node NodePorts"
  type        = bool
  default     = true
}

variable "nlb_name" {
  description = "Name for the AWS NLB"
  type        = string
  default     = "hrms-istio-nlb"
}

# Toggle and name for staging NLB (ports 8080/8443)
variable "enable_staging_nlb" {
  description = "Whether to provision a separate staging NLB (8080/8443)"
  type        = bool
  default     = true
}

variable "staging_nlb_name" {
  description = "Name for the staging AWS NLB"
  type        = string
  default     = "hrms-istio-nlb-staging"
}
