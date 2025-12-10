#!/bin/bash

# Configuration
REGION="ap-south-1"
ACCOUNT="475936984863"
ECR_SERVER="${ACCOUNT}.dkr.ecr.${REGION}.amazonaws.com"
NAMESPACES=("staging" "production") # List all namespaces here
SECRET_NAME="ecr-registry-secret"
EMAIL="docker@example.com" # Dummy email required for some k8s versions

# Logging
LOG_FILE="/var/log/ecr-refresh.log"
echo "$(date): Starting ECR secret refresh" >> $LOG_FILE

# 1. Get the ECR Password
# Note: Ensure the machine running this has IAM permissions for ecr:GetAuthorizationToken
PASSWORD=$(aws ecr get-login-password --region $REGION)

if [ -z "$PASSWORD" ]; then
    echo "$(date): Error: Failed to retrieve AWS ECR password." >> $LOG_FILE
    exit 1
fi

# 2. Loop through namespaces to refresh the secret
for NS in "${NAMESPACES[@]}"; do
    echo "$(date): Refreshing secret in namespace: $NS" >> $LOG_FILE

    # Delete existing secret (ignore if it doesn't exist)
    kubectl delete secret $SECRET_NAME -n $NS --ignore-not-found >> $LOG_FILE 2>&1

    # Create the new secret
    kubectl create secret docker-registry $SECRET_NAME \
        --docker-server=$ECR_SERVER \
        --docker-username=AWS \
        --docker-password="$PASSWORD" \
        --docker-email=$EMAIL \
        -n $NS >> $LOG_FILE 2>&1

    if [ $? -eq 0 ]; then
        echo "$(date): Successfully refreshed $SECRET_NAME in $NS" >> $LOG_FILE
    else
        echo "$(date): Failed to refresh $SECRET_NAME in $NS" >> $LOG_FILE
    fi
done

echo "$(date): ECR secret refresh completed" >> $LOG_FILE