terraform {
  backend "s3" {
    bucket         = "hrms-terraform-backend-prod"
    key            = "terraform.tfstate"
    region         = "ap-south-1"
    dynamodb_table = "hrms-terraform-locks"
    encrypt        = true
  }
}