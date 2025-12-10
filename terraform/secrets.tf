// Terraform resources to create AWS Secrets Manager secret for MySQL and an IAM user/policy

resource "random_password" "mysql_root" {
  length           = 24
  override_special = "@#%&*-_+="
}

resource "random_password" "mysql_app" {
  length           = 24
  override_special = "@#%&*-_+="
}

variable "mysql_root_password" {
  description = "Optional: provide MySQL root password. If empty, a random one is generated."
  type        = string
  default     = ""
}

variable "mysql_app_user" {
  description = "Application DB user name for HRMS"
  type        = string
  default     = "hrms_user"
}

variable "mysql_app_password" {
  description = "Optional: provide MySQL app user password. If empty, a random one is generated."
  type        = string
  default     = ""
}

resource "aws_secretsmanager_secret" "hrms_mysql" {
  name = "hrms/mysql"
  description = "MySQL credentials for HRMS services"
}

resource "aws_secretsmanager_secret_version" "hrms_mysql_version" {
  secret_id     = aws_secretsmanager_secret.hrms_mysql.id
  secret_string = jsonencode({
    MYSQL_ROOT_PASSWORD = length(var.mysql_root_password) > 0 ? var.mysql_root_password : random_password.mysql_root.result,
    MYSQL_USER          = var.mysql_app_user,
    MYSQL_PASSWORD      = length(var.mysql_app_password) > 0 ? var.mysql_app_password : random_password.mysql_app.result,
  })
}

# IAM policy allowing read-only access to the above secret (for ExternalSecrets operator)
data "aws_iam_policy_document" "externalsecret_allow_secretsmanager" {
  statement {
    sid    = "AllowGetSecretValue"
    effect = "Allow"

    actions = [
      "secretsmanager:GetSecretValue",
      "secretsmanager:DescribeSecret",
      "secretsmanager:ListSecrets",
    ]

    resources = [aws_secretsmanager_secret.hrms_mysql.arn]
  }
}

# IAM policy allowing ECR token retrieval for the ECR refresh script
data "aws_iam_policy_document" "ecr_token_access" {
  statement {
    sid    = "AllowECRTokenRetrieval"
    effect = "Allow"

    actions = [
      "ecr:GetAuthorizationToken",
    ]

    resources = ["*"]
  }
}

resource "aws_iam_policy" "externalsecret_read_policy" {
  name        = "hrms-externalsecret-read-policy"
  description = "Allows ExternalSecrets operator to read hrms/mysql secret"
  policy      = data.aws_iam_policy_document.externalsecret_allow_secretsmanager.json
}

resource "aws_iam_policy" "ecr_token_policy" {
  name        = "hrms-ecr-token-policy"
  description = "Allows EC2 instances to retrieve ECR authorization tokens"
  policy      = data.aws_iam_policy_document.ecr_token_access.json
}

# IAM user for ExternalSecrets operator (if IRSA isn't available)
// Create an IAM role that EC2 instances can assume (instance profile) so the ExternalSecrets operator
// running on those nodes can read Secrets Manager without static credentials.

data "aws_iam_policy_document" "assume_role_for_ec2" {
  statement {
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "externalsecret_node_role" {
  name               = "hrms-external-secrets-node-role"
  assume_role_policy = data.aws_iam_policy_document.assume_role_for_ec2.json
}

resource "aws_iam_role_policy_attachment" "attach_policy_to_role" {
  role       = aws_iam_role.externalsecret_node_role.name
  policy_arn = aws_iam_policy.externalsecret_read_policy.arn
}

resource "aws_iam_role_policy_attachment" "attach_ecr_policy_to_role" {
  role       = aws_iam_role.externalsecret_node_role.name
  policy_arn = aws_iam_policy.ecr_token_policy.arn
}

resource "aws_iam_instance_profile" "externalsecret_profile" {
  name = "hrms-external-secrets-instance-profile"
  role = aws_iam_role.externalsecret_node_role.name
}

output "secretsmanager_hrms_mysql_arn" {
  description = "ARN of the Secrets Manager secret for HRMS MySQL"
  value       = aws_secretsmanager_secret.hrms_mysql.arn
}

output "externalsecret_node_role_arn" {
  description = "IAM role ARN to attach to EC2 instances (instance profile)"
  value       = aws_iam_role.externalsecret_node_role.arn
}

output "externalsecret_instance_profile_name" {
  description = "Instance profile name to attach to EC2 instances"
  value       = aws_iam_instance_profile.externalsecret_profile.name
}

output "ecr_token_policy_arn" {
  description = "IAM policy ARN for ECR token access"
  value       = aws_iam_policy.ecr_token_policy.arn
}
