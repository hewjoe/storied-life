# Storied Life CloudFormation Deployment

This directory contains CloudFormation templates for deploying the Storied Life application infrastructure across multiple stacks.

## Architecture Overview

The infrastructure is split into 4 separate CloudFormation stacks to provide better modularity, dependency management, and deployment flexibility:

1. **VPC Stack** (`vpc-stack.yaml`) - Base networking infrastructure
2. **Bastion Stack** (`bastion-stack.yaml`) - Bastion host for secure access
3. **RDS Stack** (`rds-stack.yaml`) - PostgreSQL database
4. **Application Stack** (`app-stack.yaml`) - Main application infrastructure

## Stack Dependencies

The stacks must be deployed in the following order due to cross-stack dependencies:

```
vpc-stack → bastion-stack → rds-stack → app-stack
```

### Dependency Details

- **Bastion Stack** depends on VPC stack exports (subnets, KMS key)
- **RDS Stack** depends on VPC stack exports (subnets, KMS key)
- **Application Stack** depends on VPC, Bastion, and RDS stack exports (subnets, KMS key, bastion security group, RDS security group, database secret)

## Prerequisites

1. AWS CLI configured with appropriate permissions
2. An existing EC2 Key Pair for SSH access
3. A Route 53 Hosted Zone for your domain

## Environment Variables

Set these required environment variables before deployment:

```bash
export SSH_KEY_NAME="your-ec2-key-name"
export HOSTED_ZONE_ID="your-route53-hosted-zone-id"
```

Optional variables (with defaults):

```bash
export STACK_BASE_NAME="storied-life-dev"        # Base name for all stacks
export APPLICATION_NAME="storied-life-dev"        # Application name
export DOMAIN_NAME="storied-life.me"              # Your domain name
export BASTION_DESIRED_CAPACITY="0"               # 0=off, 1=on
export REGION="us-east-1"                         # AWS region
```

## Deployment Commands

### Deploy All Stacks (Recommended for New Deployments)

```bash
make deploy-all
```

This will deploy all stacks in the correct order: VPC → Bastion → RDS → Application.

### Deploy Individual Stacks

Deploy stacks individually in dependency order:

```bash
# 1. Deploy VPC (networking foundation)
make deploy-vpc

# 2. Deploy Bastion (optional, for secure access)
make deploy-bastion

# 3. Deploy RDS (database)
make deploy-rds

# 4. Deploy Application (main application)
make deploy-app
```

### Validation

Validate templates before deployment:

```bash
# Validate all templates
make validate-all

# Validate individual templates
make validate-vpc
make validate-bastion
make validate-rds
make validate-app
```

### Stack Information

View stack outputs:

```bash
# Show outputs for all stacks
make info-all

# Show outputs for individual stacks
make info-vpc
make info-bastion
make info-rds
make info-app
```

## Deletion Commands

**⚠️ Warning**: Deletion is irreversible. Always ensure you have backups of important data.

### Delete All Stacks

```bash
make delete-all
```

This will delete all stacks in reverse dependency order: Application → RDS → Bastion → VPC.

### Delete Individual Stacks

Delete stacks in reverse dependency order:

```bash
# 1. Delete Application stack first
make delete-app

# 2. Delete RDS stack
make delete-rds

# 3. Delete Bastion stack
make delete-bastion

# 4. Delete VPC stack last
make delete-vpc
```

## Stack Details

### VPC Stack

**File**: `vpc-stack.yaml`
**Stack Name**: `{STACK_BASE_NAME}-vpc`

**Resources Created**:
- VPC with public and private subnets across 2 AZs
- Internet Gateway and NAT Gateway
- Route tables and associations
- KMS key for encryption
- S3 bucket for application data

**Exports**: VPC ID, subnet IDs, KMS key ARN, S3 bucket name

### Bastion Stack

**File**: `bastion-stack.yaml`
**Stack Name**: `{STACK_BASE_NAME}-bastion`

**Resources Created**:
- Bastion security group with SSH and VPN access
- IAM role and instance profile for bastion
- Launch template for bastion instances
- Auto Scaling Group for bastion (0-1 instances)
- DNS record for bastion host (if Route 53 hosted zone provided)

**Dependencies**: VPC stack exports
**Exports**: Bastion security group ID, ASG name, IAM role ARN

### RDS Stack

**File**: `rds-stack.yaml`
**Stack Name**: `{STACK_BASE_NAME}-rds`

**Resources Created**:
- RDS security group (ingress rules added by app stack)
- DB subnet group
- Secrets Manager secret for database credentials
- PostgreSQL RDS instance with encryption

**Dependencies**: VPC stack exports
**Exports**: RDS security group ID, database endpoint, port, secret ARN, subnet group name

### Application Stack

**File**: `app-stack.yaml`
**Stack Name**: `{STACK_BASE_NAME}-app`

**Resources Created**:
- ALB security group with HTTPS access from internet
- Instance security group with access rules from ALB and bastion
- Security group ingress rules for SSH (from bastion) and database access (to RDS)
- IAM role and instance profile for application instances
- Launch template for application instances (spot instances)
- Auto Scaling Group for application instances
- Application Load Balancer with HTTPS listener
- SSL certificate via ACM with DNS validation
- DNS records for application subdomains

**Dependencies**: VPC, Bastion, and RDS stack exports
**Exports**: ALB security group ID, instance security group ID, ALB DNS name, instance role ARN, ASG name, certificate ARN

## Customization

### Modifying Stack Parameters

Each stack accepts various parameters that can be customized. Check the `Parameters` section of each CloudFormation template for available options.

### Adding New Exports

To add new exports from one stack for use in another:

1. Add the export to the `Outputs` section of the source stack
2. Use `Fn::ImportValue` in the target stack to reference the export
3. Ensure the export name follows the pattern: `{ApplicationName}-{ResourceType}-{Identifier}`

### Cross-Stack References

All cross-stack references use CloudFormation exports/imports with consistent naming:

```yaml
# Export (in source stack)
Outputs:
  VPCId:
    Value: !Ref VPC
    Export:
      Name: !Sub '${ApplicationName}-VPC-ID'

# Import (in target stack)
VpcId:
  Fn::ImportValue: !Sub '${ApplicationName}-VPC-ID'
```

## Troubleshooting

### Common Issues

1. **Export conflicts**: If you have multiple deployments, ensure `APPLICATION_NAME` is unique
2. **Missing dependencies**: Deploy stacks in the correct order (VPC → Bastion → RDS → App)
3. **DNS validation hanging**: Ensure your Route 53 hosted zone is correctly configured
4. **Spot instance interruptions**: Application uses spot instances for cost savings; they may be interrupted

### Viewing Stack Events

Monitor stack deployment progress in the AWS CloudFormation console or via CLI:

```bash
aws cloudformation describe-stack-events --stack-name {stack-name} --region {region}
```

### Rolling Back Failed Deployments

CloudFormation automatically rolls back failed deployments. To manually clean up:

```bash
aws cloudformation cancel-update-stack --stack-name {stack-name} --region {region}
```

## Security Considerations

- All EBS volumes are encrypted using the KMS key
- Database is deployed in private subnets
- Application instances are in private subnets, accessible via bastion or ALB
- Security groups follow least-privilege principles
- IAM roles have minimal required permissions

## Cost Optimization

- Uses spot instances for application servers (can save 50-90% on compute costs)
- Bastion host defaults to "off" (desired capacity = 0)
- Uses smaller instance types (t3.nano for bastion, t3.medium for app)
- Database uses db.t3.micro for development workloads 