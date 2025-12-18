# Optional AWS NLB in front of Istio ingressgateway

resource "aws_lb" "istio_nlb" {
  count                = var.enable_nlb ? 1 : 0
  name                 = var.nlb_name
  internal             = false
  load_balancer_type   = "network"
  enable_deletion_protection = false

  subnets = [aws_subnet.hrms_public_subnet.id]

  tags = {
    Name    = var.nlb_name
    Project = "HRMS"
  }
}

# Target group for HTTP -> NodePort 30080
resource "aws_lb_target_group" "istio_http_tg" {
  count     = var.enable_nlb ? 1 : 0
  name      = "${var.nlb_name}-http"
  port      = 30080
  protocol  = "TCP"
  target_type = "instance"
  vpc_id    = aws_vpc.hrms_vpc.id

  health_check {
    protocol = "TCP"
    port     = 15021
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 10
    interval            = 30
  }

  tags = {
    Name    = "${var.nlb_name}-http"
    Project = "HRMS"
  }
}

# Target group for HTTPS -> NodePort 30443
resource "aws_lb_target_group" "istio_https_tg" {
  count     = var.enable_nlb ? 1 : 0
  name      = "${var.nlb_name}-https"
  port      = 30443
  protocol  = "TCP"
  target_type = "instance"
  vpc_id    = aws_vpc.hrms_vpc.id

  health_check {
    protocol = "TCP"
    port     = 15021
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 10
    interval            = 30
  }

  tags = {
    Name    = "${var.nlb_name}-https"
    Project = "HRMS"
  }
}

# Listener 80 -> HTTP TG
resource "aws_lb_listener" "istio_http_listener" {
  count             = var.enable_nlb ? 1 : 0
  load_balancer_arn = aws_lb.istio_nlb[0].arn
  port              = 80
  protocol          = "TCP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.istio_http_tg[0].arn
  }
}

# Listener 443 -> HTTPS TG (TLS passthrough handled by Istio)
resource "aws_lb_listener" "istio_https_listener" {
  count             = var.enable_nlb ? 1 : 0
  load_balancer_arn = aws_lb.istio_nlb[0].arn
  port              = 443
  protocol          = "TCP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.istio_https_tg[0].arn
  }
}

# ---------------------------------
# Staging listeners (8080, 8443)
# Staging forwards to staging NodePort target groups (30081/30444).
# This exposes separate external ports for staging traffic and points
# the staging NLB to the staging NodePort targets on the worker nodes.
resource "aws_lb" "istio_staging_nlb" {
  count                      = var.enable_staging_nlb ? 1 : 0
  name                       = var.staging_nlb_name
  internal                   = false
  load_balancer_type         = "network"
  enable_deletion_protection = false

  subnets = [aws_subnet.hrms_public_subnet.id]

  tags = {
    Name    = var.staging_nlb_name
    Project = "HRMS"
    Env     = "staging"
  }
}

# Staging target group for HTTP -> NodePort 30080
resource "aws_lb_target_group" "istio_staging_http_tg" {
  count       = var.enable_staging_nlb ? 1 : 0
  name        = "${var.staging_nlb_name}-http"
  port        = 30081
  protocol    = "TCP"
  target_type = "instance"
  vpc_id      = aws_vpc.hrms_vpc.id

  health_check {
    protocol            = "TCP"
    port                = 15021
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 10
    interval            = 30
  }

  tags = {
    Name    = "${var.staging_nlb_name}-http"
    Project = "HRMS"
    Env     = "staging"
  }
}

# Staging target group for HTTPS -> NodePort 30443
resource "aws_lb_target_group" "istio_staging_https_tg" {
  count       = var.enable_staging_nlb ? 1 : 0
  name        = "${var.staging_nlb_name}-https"
  port        = 30444
  protocol    = "TCP"
  target_type = "instance"
  vpc_id      = aws_vpc.hrms_vpc.id

  health_check {
    protocol            = "TCP"
    port                = 15021
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 10
    interval            = 30
  }

  tags = {
    Name    = "${var.staging_nlb_name}-https"
    Project = "HRMS"
    Env     = "staging"
  }
}

resource "aws_lb_listener" "istio_staging_http_listener" {
  count             = var.enable_staging_nlb ? 1 : 0
  load_balancer_arn = aws_lb.istio_staging_nlb[0].arn
  port              = 80
  protocol          = "TCP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.istio_staging_http_tg[0].arn
  }
}

resource "aws_lb_listener" "istio_staging_https_listener" {
  count             = var.enable_staging_nlb ? 1 : 0
  load_balancer_arn = aws_lb.istio_staging_nlb[0].arn
  port              = 443
  protocol          = "TCP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.istio_staging_https_tg[0].arn
  }
}

# Attach all workers to the staging HTTP TG
resource "aws_lb_target_group_attachment" "istio_staging_http_tg_attachments" {
  count            = var.enable_staging_nlb ? length(aws_instance.k8s_workers) : 0
  target_group_arn = aws_lb_target_group.istio_staging_http_tg[0].arn
  target_id        = aws_instance.k8s_workers[count.index].id
}

# Attach all workers to the staging HTTPS TG
resource "aws_lb_target_group_attachment" "istio_staging_https_tg_attachments" {
  count            = var.enable_staging_nlb ? length(aws_instance.k8s_workers) : 0
  target_group_arn = aws_lb_target_group.istio_staging_https_tg[0].arn
  target_id        = aws_instance.k8s_workers[count.index].id
}

# Attach all workers to the HTTP TG
resource "aws_lb_target_group_attachment" "istio_http_tg_attachments" {
  count            = var.enable_nlb ? length(aws_instance.k8s_workers) : 0
  target_group_arn = aws_lb_target_group.istio_http_tg[0].arn
  target_id        = aws_instance.k8s_workers[count.index].id
}

# Attach all workers to the HTTPS TG
resource "aws_lb_target_group_attachment" "istio_https_tg_attachments" {
  count            = var.enable_nlb ? length(aws_instance.k8s_workers) : 0
  target_group_arn = aws_lb_target_group.istio_https_tg[0].arn
  target_id        = aws_instance.k8s_workers[count.index].id
}
