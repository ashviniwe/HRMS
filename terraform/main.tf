terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# VPC Configuration
resource "aws_vpc" "hrms_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "hrms-k8s-vpc"
  }
}

# Internet Gateway
resource "aws_internet_gateway" "hrms_igw" {
  vpc_id = aws_vpc.hrms_vpc.id

  tags = {
    Name = "hrms-k8s-igw"
  }
}

# Public Subnet
resource "aws_subnet" "hrms_public_subnet" {
  vpc_id                  = aws_vpc.hrms_vpc.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "${var.aws_region}a"
  map_public_ip_on_launch = true

  tags = {
    Name = "hrms-k8s-public-subnet"
  }
}

# Route Table
resource "aws_route_table" "hrms_public_rt" {
  vpc_id = aws_vpc.hrms_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.hrms_igw.id
  }

  tags = {
    Name = "hrms-k8s-public-rt"
  }
}

# Route Table Association
resource "aws_route_table_association" "hrms_public_rta" {
  subnet_id      = aws_subnet.hrms_public_subnet.id
  route_table_id = aws_route_table.hrms_public_rt.id
}

# Master Node
resource "aws_instance" "k8s_master" {
  ami           = var.ami_id
  instance_type = var.master_instance_type
  key_name      = var.key_name
  subnet_id     = aws_subnet.hrms_public_subnet.id

  vpc_security_group_ids = [aws_security_group.k8s_master_sg.id]

  root_block_device {
    volume_size = 30
    volume_type = "gp3"
  }

  tags = {
    Name = "hrms-k8s-master"
    Role = "master"
  }

  user_data = file("${path.module}/user_data.sh")
}

# Worker Nodes
resource "aws_instance" "k8s_workers" {
  count         = var.worker_count
  ami           = var.ami_id
  instance_type = var.worker_instance_type
  key_name      = var.key_name
  subnet_id     = aws_subnet.hrms_public_subnet.id

  vpc_security_group_ids = [aws_security_group.k8s_worker_sg.id]

  root_block_device {
    volume_size = 50
    volume_type = "gp3"
  }

  tags = {
    Name = "hrms-k8s-worker-${count.index + 1}"
    Role = "worker"
  }

  user_data = file("${path.module}/user_data.sh")
}
