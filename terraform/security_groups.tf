# Fetch existing Elastic IP by Name tag
data "aws_eip" "monitor_sys_eip" {
  filter {
    name   = "tag:Name"
    values = ["monitor_sys_eip"]
  }
}

# Master Node Security Group
resource "aws_security_group" "k8s_master_sg" {
  name        = "hrms-k8s-master-sg"
  description = "Security group for K8s master node"
  vpc_id      = aws_vpc.hrms_vpc.id

  # SSH
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Kubernetes API
  ingress {
    from_port   = 6443
    to_port     = 6443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # etcd
  ingress {
    from_port   = 2379
    to_port     = 2380
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/16"]
  }

  # Kubelet API, kube-scheduler, kube-controller-manager
  ingress {
    from_port   = 10250
    to_port     = 10259
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/16"]
  }

  # Allow Prometheus Security Group to access ArgoCD Metrics 
  ingress {
    from_port   = 32083
    to_port     = 32083
    protocol    = "tcp"
    cidr_blocks = ["${data.aws_eip.monitor_sys_eip.public_ip}/32"]   # Prometheus public IP
  }
  
  # Allow Prometheus Security Group to access Node Exporter
  ingress {
    from_port   = 9100
    to_port     = 9100
    protocol    = "tcp"
    cidr_blocks = ["${data.aws_eip.monitor_sys_eip.public_ip}/32"]   # Prometheus public IP
  }

  # NodePort Services
  ingress {
    from_port   = 30000
    to_port     = 32767
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Flannel/Calico
  ingress {
    from_port   = 8472
    to_port     = 8472
    protocol    = "udp"
    cidr_blocks = ["10.0.0.0/16"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "hrms-k8s-master-sg"
  }
}

# Worker Node Security Group
resource "aws_security_group" "k8s_worker_sg" {
  name        = "hrms-k8s-worker-sg"
  description = "Security group for K8s worker nodes"
  vpc_id      = aws_vpc.hrms_vpc.id

  # SSH
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Kubelet API
  ingress {
    from_port   = 10250
    to_port     = 10250
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/16"]
  }

  # NodePort Services
  ingress {
    from_port   = 30000
    to_port     = 32767
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Flannel/Calico
  ingress {
    from_port   = 8472
    to_port     = 8472
    protocol    = "udp"
    cidr_blocks = ["10.0.0.0/16"]
  }

  # Allow Prometheus Security Group to access Node Exporter
  ingress {
    from_port   = 9100
    to_port     = 9100
    protocol    = "tcp"
    cidr_blocks = ["${data.aws_eip.monitor_sys_eip.public_ip}/32"]   # Prometheus public IP
  }
  
  # Allow all from master
  ingress {
    from_port       = 0
    to_port         = 0
    protocol        = "-1"
    security_groups = [aws_security_group.k8s_master_sg.id]
  }

  # Allow all between workers
  ingress {
    from_port = 0
    to_port   = 0
    protocol  = "-1"
    self      = true
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "hrms-k8s-worker-sg"
  }
}

# Explicitly allow HTTP/HTTPS NodePorts on workers from configured sources
resource "aws_security_group_rule" "worker_http_nodeports" {
  # for_each must be a map or a set of strings; cast numbers to strings
  for_each          = toset([for p in var.http_nodeports : tostring(p)])
  type              = "ingress"
  from_port         = tonumber(each.value)
  to_port           = tonumber(each.value)
  protocol          = "tcp"
  security_group_id = aws_security_group.k8s_worker_sg.id
  cidr_blocks       = var.allowed_http_nodeports_cidrs
  description       = "Allow HTTP/S NodePort ${each.value} from allowed CIDRs"
}

# Allow Istio ingress gateway health checks (port 15021) on workers
resource "aws_security_group_rule" "worker_istio_health" {
  type              = "ingress"
  from_port         = 15021
  to_port           = 15021
  protocol          = "tcp"
  security_group_id = aws_security_group.k8s_worker_sg.id
  cidr_blocks       = var.allowed_istio_health_cidrs
  description       = "Allow Istio health check port 15021 from allowed CIDRs"
}
