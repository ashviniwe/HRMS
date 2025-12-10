# ECR Secret Refresh Setup

This directory contains the script and playbook for automatically refreshing AWS ECR registry secrets in Kubernetes.

## Files

- `refresh-ecr-secrets.sh` - The bash script that refreshes ECR secrets in staging and production namespaces
- `../playbooks/05-setup-ecr-refresh.yml` - Standalone Ansible playbook for setting up ECR refresh

## What it does

The ECR refresh script:
1. Retrieves a new ECR authorization token from AWS
2. Deletes existing `ecr-registry-secret` secrets in staging and production namespaces
3. Creates new docker-registry secrets with the updated token
4. Logs all operations to `/var/log/ecr-refresh.log`

## Automatic Setup

The ECR refresh is automatically set up when running the master node setup playbook (`02-setup-master.yml`). This includes:
- Copying the refresh script to `/opt/k8s-scripts/`
- Setting up a cron job to run every 6 hours
- Running the script once during setup to initialize secrets

## Manual Setup

If you need to set up or reconfigure ECR refresh separately, run:

```bash
ansible-playbook -i inventory 05-setup-ecr-refresh.yml
```

## Cron Schedule

The script runs automatically every 6 hours:
- 00:00 (midnight)
- 06:00 (6 AM)
- 12:00 (noon)
- 18:00 (6 PM)

## Configuration

Update the following variables in `refresh-ecr-secrets.sh` if needed:
- `REGION` - AWS region (currently: ap-south-1)
- `ACCOUNT` - AWS account ID (currently: 475936984863)
- `NAMESPACES` - List of Kubernetes namespaces (currently: staging, production)
- `SECRET_NAME` - Name of the docker registry secret (currently: ecr-registry-secret)

## Prerequisites

The master node must have:
- AWS CLI installed and configured
- IAM permissions for `ecr:GetAuthorizationToken`
- kubectl access to the cluster
- Both `staging` and `production` namespaces created

## Monitoring

Check logs at `/var/log/ecr-refresh.log` on the master node:

```bash
# View recent logs
tail -f /var/log/ecr-refresh.log

# Check cron job status
sudo crontab -l | grep ecr-refresh

# Manually run the script for testing
sudo /opt/k8s-scripts/refresh-ecr-secrets.sh
```

## Troubleshooting

1. **AWS credentials not configured**: Ensure the master node has AWS CLI configured with appropriate credentials
2. **Permission denied**: Make sure the script has executable permissions (`chmod +x /opt/k8s-scripts/refresh-ecr-secrets.sh`)
3. **Namespace not found**: Ensure staging and production namespaces exist in your cluster
4. **Cron not working**: Check if cron service is running (`systemctl status cron`)

## Security Notes

- The ECR token is temporary and expires, which is why regular refresh is needed
- The script runs as root to ensure it has necessary permissions for kubectl operations
- All operations are logged for audit purposes