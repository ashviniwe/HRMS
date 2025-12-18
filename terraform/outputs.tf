output "master_public_ip" {
  value = aws_instance.k8s_master.public_ip
}

output "master_private_ip" {
  value = aws_instance.k8s_master.private_ip
}

output "worker_public_ips" {
  value = aws_instance.k8s_workers[*].public_ip
}

output "worker_private_ips" {
  value = aws_instance.k8s_workers[*].private_ip
}

output "istio_nlb_dns_name" {
  value       = try(aws_lb.istio_nlb[0].dns_name, null)
  description = "DNS name of the provisioned NLB (if enabled)"
}
