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

resource "aws_iam_policy" "externalsecret_read_policy" {
  name        = "hrms-externalsecret-read-policy"
  description = "Allows ExternalSecrets operator to read hrms/mysql secret"
  policy      = data.aws_iam_policy_document.externalsecret_allow_secretsmanager.json
}

# IAM user for ExternalSecrets operator (if IRSA isn't available)
resource "aws_iam_user" "externalsecret_user" {
  name = "hrms-external-secrets-operator"
}

resource "aws_iam_user_policy_attachment" "externalsecret_attach" {
  user       = aws_iam_user.externalsecret_user.name
  policy_arn = aws_iam_policy.externalsecret_read_policy.arn
}

resource "aws_iam_access_key" "externalsecret_key" {
  user = aws_iam_user.externalsecret_user.name
}

output "secretsmanager_hrms_mysql_arn" {
  description = "ARN of the Secrets Manager secret for HRMS MySQL"
  value       = aws_secretsmanager_secret.hrms_mysql.arn
}

output "externalsecret_iam_user" {
  description = "IAM user created for ExternalSecrets operator (use for access keys if not using IRSA)"
  value       = aws_iam_user.externalsecret_user.name
}

output "externalsecret_access_key_id" {
  description = "Access key id for ExternalSecrets operator (sensitive)"
  value       = aws_iam_access_key.externalsecret_key.id
  sensitive   = true
}

output "externalsecret_secret_access_key" {
  description = "Secret access key for ExternalSecrets operator (sensitive)"
  value       = aws_iam_access_key.externalsecret_key.secret
  sensitive   = true
}
