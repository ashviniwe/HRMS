# -----------------------------
# ECR Repositories
# -----------------------------
resource "aws_ecr_repository" "hrms_employee_service" {
  name = "hrms/employee-service"
}

resource "aws_ecr_repository" "hrms_attendance_service" {
  name = "hrms/attendance-service"
}

resource "aws_ecr_repository" "hrms_audit_service" {
  name = "hrms/audit-service"
}

resource "aws_ecr_repository" "hrms_compliance_service" {
  name = "hrms/compliance-service"
}

resource "aws_ecr_repository" "hrms_frontend" {
  name = "hrms/frontend"
}

resource "aws_ecr_repository" "hrms_leave_service" {
  name = "hrms/leave-service"
}

resource "aws_ecr_repository" "hrms_notification_service" {
  name = "hrms/notification-service"
}

resource "aws_ecr_repository" "hrms_user_service" {
  name = "hrms/user-service"
}

# -----------------------------
# ECR Lifecycle Policies
# -----------------------------
locals {
  lifecycle_policy = <<EOF
{
  "rules": [
    {
      "rulePriority": 1,
      "description": "Expire untagged images older than 14 days",
      "selection": {
        "tagStatus": "untagged",
        "countType": "sinceImagePushed",
        "countUnit": "days",
        "countNumber": 14
      },
      "action": {
        "type": "expire"
      }
    },
    {
      "rulePriority": 2,
      "description": "Keep only the last 10 tagged images",
      "selection": {
        "tagStatus": "tagged",
        "tagPatternList": ["*"],
        "countType": "imageCountMoreThan",
        "countNumber": 10
      },
      "action": {
        "type": "expire"
      }
    }
  ]
}
EOF
}

resource "aws_ecr_lifecycle_policy" "hrms_employee_service_policy" {
  repository = aws_ecr_repository.hrms_employee_service.name
  policy     = local.lifecycle_policy
}

resource "aws_ecr_lifecycle_policy" "hrms_attendance_service_policy" {
  repository = aws_ecr_repository.hrms_attendance_service.name
  policy     = local.lifecycle_policy
}

resource "aws_ecr_lifecycle_policy" "hrms_audit_service_policy" {
  repository = aws_ecr_repository.hrms_audit_service.name
  policy     = local.lifecycle_policy
}

resource "aws_ecr_lifecycle_policy" "hrms_compliance_service_policy" {
  repository = aws_ecr_repository.hrms_compliance_service.name
  policy     = local.lifecycle_policy
}

resource "aws_ecr_lifecycle_policy" "hrms_frontend_policy" {
  repository = aws_ecr_repository.hrms_frontend.name
  policy     = local.lifecycle_policy
}

resource "aws_ecr_lifecycle_policy" "hrms_leave_service_policy" {
  repository = aws_ecr_repository.hrms_leave_service.name
  policy     = local.lifecycle_policy
}

resource "aws_ecr_lifecycle_policy" "hrms_notification_service_policy" {
  repository = aws_ecr_repository.hrms_notification_service.name
  policy     = local.lifecycle_policy
}

resource "aws_ecr_lifecycle_policy" "hrms_user_service_policy" {
  repository = aws_ecr_repository.hrms_user_service.name
  policy     = local.lifecycle_policy
}