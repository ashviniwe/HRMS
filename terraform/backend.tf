// Production backend for HRMS infrastructure
// This config stores the Terraform state in S3 and uses DynamoDB for state locking.
// Do NOT store credentials here; provide them via environment variables or instance roles.
terraform {
  backend "s3" {
    bucket         = "hrms-terraform-backend-singapore-prod"
    key            = "terraform.tfstate"
    region         = "ap-southeast-1"
    dynamodb_table = "hrms-terraform-locks-sg"
    encrypt        = true
  }
}
