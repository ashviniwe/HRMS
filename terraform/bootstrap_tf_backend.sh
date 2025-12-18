#!/bin/bash

set -euo pipefail

# ---------------------------------------------------------
# CONFIGURATION (allow overrides via environment variables)
# ---------------------------------------------------------
# Use environment variables to allow running this script for dev/staging/prod
# Examples:
#  AWS_REGION=us-east-1 TERRAFORM_BUCKET_NAME=hrms-tf-backend-staging \
#    TERRAFORM_DYNAMO_TABLE=hrms-tf-locks ./bootstrap_tf_backend.sh
AWS_REGION="${AWS_REGION:-ap-southeast-1}"
BUCKET_NAME="${TERRAFORM_BUCKET_NAME:-hrms-terraform-backend-singapore-prod}"
DYNAMO_TABLE="${TERRAFORM_DYNAMO_TABLE:-hrms-terraform-locks-sg}"

echo ""
echo "============================================"
echo "   Terraform Backend Bootstrap (S3+Dynamo)   "
echo "============================================"
echo "Region       : $AWS_REGION"
echo "S3 Bucket    : $BUCKET_NAME"
echo "Dynamo Table : $DYNAMO_TABLE"
echo ""

# ---------------------------------------------------------
# Better error reporting for common AWS CLI failures
trap 'echo "❌ Error: AWS CLI command failed. Check AWS credentials and IAM permissions."; exit 1' ERR

# ---------------------------------------------------------
# CHECK AWS CLI
# ---------------------------------------------------------
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI not installed. Please install it first."
    exit 1
fi

# ---------------------------------------------------------
# CREATE S3 BUCKET (IDEMPOTENT)
# ---------------------------------------------------------
echo "[1/5] Checking S3 bucket '$BUCKET_NAME'..."

if aws s3api head-bucket --bucket "$BUCKET_NAME" 2>/dev/null; then
    echo "✔ S3 bucket already exists."
else
    echo "➜ Creating S3 bucket..."
    
    # Handle us-east-1 edge case (does not allow LocationConstraint)
    if [ "$AWS_REGION" == "us-east-1" ]; then
        aws s3api create-bucket --bucket "$BUCKET_NAME" --region "$AWS_REGION"
    else
        aws s3api create-bucket \
            --bucket "$BUCKET_NAME" \
            --region "$AWS_REGION" \
            --create-bucket-configuration LocationConstraint="$AWS_REGION"
    fi

    echo "➜ Enabling versioning..."
    aws s3api put-bucket-versioning \
        --bucket "$BUCKET_NAME" \
        --versioning-configuration Status=Enabled

    echo "➜ Enabling SSE-S3 encryption..."
    aws s3api put-bucket-encryption \
        --bucket "$BUCKET_NAME" \
        --server-side-encryption-configuration '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"AES256"}}]}'

    echo "➜ Blocking public access..."
    aws s3api put-public-access-block \
        --bucket "$BUCKET_NAME" \
        --public-access-block-configuration "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"

    echo "✔ S3 bucket created and secured."
fi

# ---------------------------------------------------------
# APPLY LIFECYCLE RULE (CLEAN OLD VERSIONS)
# ---------------------------------------------------------
echo ""
echo "[2/5] Applying lifecycle rule..."
# Cleans up non-current versions after 90 days to save costs
# Warning: Non-current state versions will be deleted after 90 days.
# Ensure you have a backup strategy for critical state files if required.
echo "Note: Non-current state versions will be deleted after 90 days."
aws s3api put-bucket-lifecycle-configuration \
    --bucket "$BUCKET_NAME" \
    --lifecycle-configuration '{
        "Rules": [
            {
                "ID": "ExpireOldStateVersions",
                "Status": "Enabled",
                "Filter": { "Prefix": "" },
                "NoncurrentVersionExpiration": { "NoncurrentDays": 90 }
            }
        ]
    }'
echo "✔ Lifecycle rule applied (90-day retention for old versions)."

# ---------------------------------------------------------
# CREATE DYNAMODB TABLE (IDEMPOTENT)
# ---------------------------------------------------------
echo ""
echo "[3/5] Checking DynamoDB table '$DYNAMO_TABLE'..."

if aws dynamodb describe-table --table-name "$DYNAMO_TABLE" >/dev/null 2>&1; then
    echo "✔ DynamoDB table already exists."
else
    echo "➜ Creating DynamoDB table..."
    aws dynamodb create-table \
        --table-name "$DYNAMO_TABLE" \
        --attribute-definitions AttributeName=LockID,AttributeType=S \
        --key-schema AttributeName=LockID,KeyType=HASH \
        --billing-mode PAY_PER_REQUEST

    echo "➜ Waiting for DynamoDB table to become ACTIVE..."
    aws dynamodb wait table-exists --table-name "$DYNAMO_TABLE"

    echo "✔ DynamoDB lock table created."
fi

# ---------------------------------------------------------
# ENABLE DELETION PROTECTION
# ---------------------------------------------------------
echo "[4/5] Enabling deletion protection..."
aws dynamodb update-table \
    --table-name "$DYNAMO_TABLE" \
    --region "$AWS_REGION" \
    --deletion-protection-enabled
echo "✔ Deletion protection enabled."

# ---------------------------------------------------------
# ENABLE POINT-IN-TIME RECOVERY (PITR)
# ---------------------------------------------------------
echo "[5/5] Enabling point-in-time recovery (PITR)..."
aws dynamodb update-continuous-backups \
    --table-name "$DYNAMO_TABLE" \
    --region "$AWS_REGION" \
    --point-in-time-recovery-specification PointInTimeRecoveryEnabled=true
echo "✔ PITR enabled (can restore to any second in the last 35 days)."

echo ""
echo "============================================"
echo "      Terraform backend bootstrap done       "
echo "============================================"
echo "You can now run: terraform init"
echo ""
