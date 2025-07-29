# -----------------------------------------------------------------------------
# Makefile for deploying the Storied Life CloudFormation stacks
#
# Usage:
#   make deploy-all   - Deploy all stacks in order (vpc, bastion, rds, app).
#   make deploy-vpc   - Deploy only the VPC stack.
#   make deploy-bastion - Deploy only the bastion stack.
#   make deploy-rds   - Deploy only the RDS stack.
#   make deploy-app   - Deploy only the application stack.
#   make delete-all   - Delete all stacks in reverse order.
#   make delete-vpc   - Delete only the VPC stack.
#   make delete-bastion - Delete only the bastion stack.
#   make delete-rds   - Delete only the RDS stack.
#   make delete-app   - Delete only the application stack.
#   make validate-all - Validate all CloudFormation templates.
#   make info-all     - Show outputs for all stacks.
#   make get-bastion-key - Retrieve bastion private key from SSM and save to ~/.ssh/
#   make get-app-key  - Retrieve application private key from SSM and save to ~/.ssh/
#   make help         - Show this help message.
#
# Before running any deploy commands, you must set the following variables:
#   export HOSTED_ZONE_ID="your-route53-hosted-zone-id"
# -----------------------------------------------------------------------------

# Use bash instead of sh for better compatibility
SHELL := /bin/bash

# --- Configuration ---
# The base name for the CloudFormation stacks.
STACK_BASE_NAME ?= storied-life

# Individual stack names
VPC_STACK_NAME     := $(STACK_BASE_NAME)-vpc
BASTION_STACK_NAME := $(STACK_BASE_NAME)-bastion
RDS_STACK_NAME     := $(STACK_BASE_NAME)-rds
APP_STACK_NAME     := $(STACK_BASE_NAME)-app

# The AWS Region to deploy to.
REGION          ?= us-east-1

# The paths to the CloudFormation templates.
VPC_TEMPLATE     := vpc-stack.yaml
BASTION_TEMPLATE := bastion-stack.yaml
RDS_TEMPLATE     := rds-stack.yaml
APP_TEMPLATE     := app-stack.yaml

# The domain name for the application.
DOMAIN_NAME     ?= storied-life.me

# Hosted zone id
HOSTED_ZONE_ID  ?= Z0543210ZPXYHBQV5U0X

# The name of the application.
APPLICATION_NAME ?= storied-life-dev

# --- Optional/Auto-detected Variables ---
# Automatically detect the public IP of the user running this command.
# This can be overridden, e.g., `make deploy-vpc MY_SSH_CIDR_IP=8.8.8.8/32`
MY_IP           := $(shell curl -s http://checkip.amazonaws.com)
MY_SSH_CIDR_IP  ?= $(MY_IP)/32

# Set to 1 to launch the bastion host on deploy.
# Example: `make deploy-bastion BASTION_DESIRED_CAPACITY=1`
BASTION_DESIRED_CAPACITY ?= 0

# --- Required Variables Checks ---
# These are checked only for targets that need them
define check_hosted_zone
	@if [ -z "$(HOSTED_ZONE_ID)" ]; then \
		echo "❌ ERROR: HOSTED_ZONE_ID is not set. Please set it in your environment."; \
		echo "   Example: export HOSTED_ZONE_ID='Z2FDTNDATAQYW2'"; \
		exit 1; \
	fi
endef

# --- Targets ---
.PHONY: all help deploy-all deploy-vpc deploy-bastion deploy-rds deploy-app delete-all delete-vpc delete-bastion delete-rds delete-app validate-all validate-vpc validate-bastion validate-rds validate-app info-all info-vpc info-bastion info-rds info-app get-bastion-key get-app-key

all: help

help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "Deploy Targets:"
	@echo "  deploy-all      Deploy all stacks in order (vpc → bastion → rds → app)"
	@echo "  deploy-vpc      Deploy only the VPC stack"
	@echo "  deploy-bastion  Deploy only the bastion stack"
	@echo "  deploy-rds      Deploy only the RDS stack"
	@echo "  deploy-app      Deploy only the application stack"
	@echo ""
	@echo "Delete Targets:"
	@echo "  delete-all      Delete all stacks in reverse order (app → rds → bastion → vpc)"
	@echo "  delete-vpc      Delete only the VPC stack"
	@echo "  delete-bastion  Delete only the bastion stack"
	@echo "  delete-rds      Delete only the RDS stack"
	@echo "  delete-app      Delete only the application stack"
	@echo ""
	@echo "Validate Targets:"
	@echo "  validate-all    Validate all CloudFormation templates"
	@echo "  validate-vpc    Validate VPC template"
	@echo "  validate-bastion Validate bastion template"
	@echo "  validate-rds    Validate RDS template"
	@echo "  validate-app    Validate application template"
	@echo ""
	@echo "Info Targets:"
	@echo "  info-all        Show outputs for all stacks"
	@echo "  info-vpc        Show VPC stack outputs"
	@echo "  info-bastion    Show bastion stack outputs"
	@echo "  info-rds        Show RDS stack outputs"
	@echo "  info-app        Show application stack outputs"
	@echo ""
	@echo "SSH Key Management:"
	@echo "  get-bastion-key Retrieve bastion private key from SSM and save to ~/.ssh/"
	@echo "  get-app-key     Retrieve application private key from SSM and save to ~/.ssh/"
	@echo ""
	@echo "Required Environment Variables (for deploy targets):"
	@echo "  HOSTED_ZONE_ID    (e.g., 'export HOSTED_ZONE_ID=Z2FDTNDATAQYW2')"
	@echo ""
	@echo "Optional Variables:"
	@echo "  STACK_BASE_NAME            (default: storied-life-dev)"
	@echo "  APPLICATION_NAME           (default: storied-life-dev)"
	@echo "  DOMAIN_NAME                (default: storied-life.me)"
	@echo "  MY_SSH_CIDR_IP             (default: auto-detected)"
	@echo "  BASTION_DESIRED_CAPACITY   (default: 0)"
	@echo ""

# --- Deploy Targets ---
deploy-all: deploy-vpc deploy-bastion deploy-rds deploy-app
	@echo "🎉 All stacks deployed successfully!"

deploy-vpc: validate-vpc
	@echo "🚀 Deploying VPC stack [$(VPC_STACK_NAME)] to region [$(REGION)]..."
	@echo "💻 Allowing SSH access from: [$(MY_SSH_CIDR_IP)]"
	@aws cloudformation deploy \
		--region $(REGION) \
		--template-file $(VPC_TEMPLATE) \
		--stack-name $(VPC_STACK_NAME) \
		--capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
		--parameter-overrides \
			ApplicationName=$(APPLICATION_NAME) \
			MySshCidrIp=$(MY_SSH_CIDR_IP) \
			HostedZoneId=$(HOSTED_ZONE_ID)
	@echo "✅ VPC stack deployment initiated."

deploy-bastion: validate-bastion
	$(call check_hosted_zone)
	@echo "🚀 Deploying bastion stack [$(BASTION_STACK_NAME)] to region [$(REGION)]..."
	@echo "🌍 Using Hosted Zone ID: [$(HOSTED_ZONE_ID)]"
	@aws cloudformation deploy \
		--region $(REGION) \
		--template-file $(BASTION_TEMPLATE) \
		--stack-name $(BASTION_STACK_NAME) \
		--capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
		--parameter-overrides \
			ApplicationName=$(APPLICATION_NAME) \
			HostedZoneId=$(HOSTED_ZONE_ID) \
			MySshCidrIp=$(MY_SSH_CIDR_IP) \
			BastionDesiredCapacity=$(BASTION_DESIRED_CAPACITY)
	@echo "✅ Bastion stack deployment initiated."

deploy-rds: validate-rds
	@echo "🚀 Deploying RDS stack [$(RDS_STACK_NAME)] to region [$(REGION)]..."
	@aws cloudformation deploy \
		--region $(REGION) \
		--template-file $(RDS_TEMPLATE) \
		--stack-name $(RDS_STACK_NAME) \
		--capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
		--parameter-overrides \
			ApplicationName=$(APPLICATION_NAME)
	@echo "✅ RDS stack deployment initiated."

deploy-app: validate-app
	$(call check_hosted_zone)
	@echo "🚀 Deploying application stack [$(APP_STACK_NAME)] to region [$(REGION)]..."
	@echo "🌍 Using Hosted Zone ID: [$(HOSTED_ZONE_ID)]"
	@aws cloudformation deploy \
		--region $(REGION) \
		--template-file $(APP_TEMPLATE) \
		--stack-name $(APP_STACK_NAME) \
		--capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
		--parameter-overrides \
			ApplicationName=$(APPLICATION_NAME) \
			HostedZoneId=$(HOSTED_ZONE_ID) \
			DomainName=$(DOMAIN_NAME)
	@echo "✅ Application stack deployment initiated."

# --- SSH Key Management ---
get-bastion-key:
	@echo "🔑 Retrieving bastion private key from SSM Parameter Store..."
	@mkdir -p ~/.ssh
	$(eval BASTION_KEY_ID := $(shell aws ec2 describe-key-pairs --region $(REGION) --filters Name=key-name,Values=$(APPLICATION_NAME)-bastion-keypair --query KeyPairs[*].KeyPairId --output text))
	@if [ -z "$(BASTION_KEY_ID)" ]; then \
		echo "❌ ERROR: Bastion key pair not found. Make sure the bastion stack is deployed."; \
		exit 1; \
	fi
	@aws ssm get-parameter \
		--region $(REGION) \
		--name "/ec2/keypair/$(BASTION_KEY_ID)" \
		--with-decryption \
		--query "Parameter.Value" \
		--output text > ~/.ssh/$(APPLICATION_NAME)-bastion-key
	@chmod 600 ~/.ssh/$(APPLICATION_NAME)-bastion-key
	@echo "✅ Bastion private key saved to: ~/.ssh/$(APPLICATION_NAME)-bastion-key"
	@echo "💡 You can now connect to the bastion host using:"
	@echo "   ssh -i ~/.ssh/$(APPLICATION_NAME)-bastion-key ubuntu@bastion.$(DOMAIN_NAME)"

get-app-key:
	@echo "🔑 Retrieving application private key from SSM Parameter Store..."
	@mkdir -p ~/.ssh
	$(eval APP_KEY_ID := $(shell aws ec2 describe-key-pairs --region $(REGION) --filters Name=key-name,Values=$(APPLICATION_NAME)-app-keypair --query KeyPairs[*].KeyPairId --output text))
	@if [ -z "$(APP_KEY_ID)" ]; then \
		echo "❌ ERROR: Application key pair not found. Make sure the application stack is deployed."; \
		exit 1; \
	fi
	@aws ssm get-parameter \
		--region $(REGION) \
		--name "/ec2/keypair/$(APP_KEY_ID)" \
		--with-decryption \
		--query "Parameter.Value" \
		--output text > ~/.ssh/$(APPLICATION_NAME)-app-key
	@chmod 600 ~/.ssh/$(APPLICATION_NAME)-app-key
	@echo "✅ Application private key saved to: ~/.ssh/$(APPLICATION_NAME)-app-key"
	@echo "💡 You can use this key to connect to application instances via the bastion host"

# --- Delete Targets ---
delete-all: delete-app delete-rds delete-bastion delete-vpc
	@echo "🗑️  All stacks deletion initiated!"

delete-vpc:
	@echo "🔥 Deleting VPC stack [$(VPC_STACK_NAME)] from region [$(REGION)]..."
	@read -p "Are you sure? This action is irreversible. [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		aws cloudformation delete-stack \
			--region $(REGION) \
			--stack-name $(VPC_STACK_NAME); \
		echo "✅ VPC stack deletion initiated."; \
	else \
		echo "Deletion aborted."; \
	fi

delete-bastion:
	@echo "🔥 Deleting bastion stack [$(BASTION_STACK_NAME)] from region [$(REGION)]..."
	@read -p "Are you sure? This action is irreversible. [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		aws cloudformation delete-stack \
			--region $(REGION) \
			--stack-name $(BASTION_STACK_NAME); \
		echo "✅ Bastion stack deletion initiated."; \
	else \
		echo "Deletion aborted."; \
	fi

delete-rds:
	@echo "🔥 Deleting RDS stack [$(RDS_STACK_NAME)] from region [$(REGION)]..."
	@read -p "Are you sure? This action is irreversible. [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		aws cloudformation delete-stack \
			--region $(REGION) \
			--stack-name $(RDS_STACK_NAME); \
		echo "✅ RDS stack deletion initiated."; \
	else \
		echo "Deletion aborted."; \
	fi

delete-app:
	@echo "🔥 Deleting application stack [$(APP_STACK_NAME)] from region [$(REGION)]..."
	@read -p "Are you sure? This action is irreversible. [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		aws cloudformation delete-stack \
			--region $(REGION) \
			--stack-name $(APP_STACK_NAME); \
		echo "✅ Application stack deletion initiated."; \
	else \
		echo "Deletion aborted."; \
	fi

# --- Validation Targets ---
validate-all: validate-vpc validate-bastion validate-rds validate-app
	@echo "✅ All templates validated successfully!"

validate-vpc:
	@echo "🔎 Validating VPC template [$(VPC_TEMPLATE)]..."
	@aws cloudformation validate-template \
		--region $(REGION) \
		--template-body file://$(VPC_TEMPLATE) > /dev/null
	@echo "✅ VPC template is valid."

validate-bastion:
	@echo "🔎 Validating bastion template [$(BASTION_TEMPLATE)]..."
	@aws cloudformation validate-template \
		--region $(REGION) \
		--template-body file://$(BASTION_TEMPLATE) > /dev/null
	@echo "✅ Bastion template is valid."

validate-rds:
	@echo "🔎 Validating RDS template [$(RDS_TEMPLATE)]..."
	@aws cloudformation validate-template \
		--region $(REGION) \
		--template-body file://$(RDS_TEMPLATE) > /dev/null
	@echo "✅ RDS template is valid."

validate-app:
	@echo "🔎 Validating application template [$(APP_TEMPLATE)]..."
	@aws cloudformation validate-template \
		--region $(REGION) \
		--template-body file://$(APP_TEMPLATE) > /dev/null
	@echo "✅ Application template is valid."

# --- Info Targets ---
info-all: info-vpc info-bastion info-rds info-app

info-vpc:
	@echo "ℹ️  Fetching outputs for VPC stack [$(VPC_STACK_NAME)]..."
	@aws cloudformation describe-stacks \
		--region $(REGION) \
		--stack-name $(VPC_STACK_NAME) \
		--query "Stacks[0].Outputs" \
		--output table 2>/dev/null || echo "❌ VPC stack not found or no outputs available."

info-bastion:
	@echo "ℹ️  Fetching outputs for bastion stack [$(BASTION_STACK_NAME)]..."
	@aws cloudformation describe-stacks \
		--region $(REGION) \
		--stack-name $(BASTION_STACK_NAME) \
		--query "Stacks[0].Outputs" \
		--output table 2>/dev/null || echo "❌ Bastion stack not found or no outputs available."

info-rds:
	@echo "ℹ️  Fetching outputs for RDS stack [$(RDS_STACK_NAME)]..."
	@aws cloudformation describe-stacks \
		--region $(REGION) \
		--stack-name $(RDS_STACK_NAME) \
		--query "Stacks[0].Outputs" \
		--output table 2>/dev/null || echo "❌ RDS stack not found or no outputs available."

info-app:
	@echo "ℹ️  Fetching outputs for application stack [$(APP_STACK_NAME)]..."
	@aws cloudformation describe-stacks \
		--region $(REGION) \
		--stack-name $(APP_STACK_NAME) \
		--query "Stacks[0].Outputs" \
		--output table 2>/dev/null || echo "❌ Application stack not found or no outputs available."
