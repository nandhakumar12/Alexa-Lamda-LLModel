# Voice Assistant AI - Makefile
# Production-ready voice assistant with Alexa integration

.PHONY: help install clean lint test build package deploy deploy-infra deploy-app dev logs monitor

# Default target
help: ## Show this help message
	@echo "Voice Assistant AI - Available Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Environment variables
AWS_REGION ?= us-east-1
ENVIRONMENT ?= dev
PROJECT_NAME ?= voice-assistant-ai

# Installation and setup
install: ## Install all dependencies
	@echo "Installing Python dependencies..."
	pip install -r requirements.txt
	@echo "Installing pre-commit hooks..."
	pre-commit install
	@echo "Installing Node.js dependencies..."
	cd frontend && npm install
	@echo "Installing Terraform..."
	@which terraform || (echo "Please install Terraform manually" && exit 1)

clean: ## Clean build artifacts and temporary files
	@echo "Cleaning Python cache..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	@echo "Cleaning build directories..."
	rm -rf build/ dist/ .coverage htmlcov/
	@echo "Cleaning Lambda packages..."
	rm -rf backend/lambda_functions/*/package/
	rm -f backend/lambda_functions/*/*.zip
	@echo "Cleaning Terraform state..."
	cd infra/terraform && rm -rf .terraform/ *.tfplan
	@echo "Cleaning Node.js dependencies..."
	cd frontend && rm -rf node_modules/ build/

# Code quality
lint: ## Run linting and formatting
	@echo "Running Python linting..."
	black backend/ --check
	flake8 backend/
	isort backend/ --check-only
	@echo "Running Terraform formatting..."
	cd infra/terraform && terraform fmt -check -recursive
	@echo "Running JavaScript linting..."
	cd frontend && npm run lint
	@echo "Running security checks..."
	bandit -r backend/ -f json -o bandit-report.json

format: ## Format code
	@echo "Formatting Python code..."
	black backend/
	isort backend/
	@echo "Formatting Terraform code..."
	cd infra/terraform && terraform fmt -recursive
	@echo "Formatting JavaScript code..."
	cd frontend && npm run format

# Testing
test: ## Run all tests
	@echo "Running Python tests..."
	pytest backend/tests/ -v --cov=backend --cov-report=html --cov-report=term
	@echo "Running Terraform validation..."
	cd infra/terraform && terraform init -backend=false && terraform validate
	@echo "Running JavaScript tests..."
	cd frontend && npm test -- --coverage --watchAll=false

test-unit: ## Run unit tests only
	pytest backend/tests/unit/ -v

test-integration: ## Run integration tests
	pytest backend/tests/integration/ -v

# Build and package
build: ## Build all components
	@echo "Building Lambda functions..."
	$(MAKE) package-lambdas
	@echo "Building frontend..."
	cd frontend && npm run build

package-lambdas: ## Package Lambda functions
	@echo "Packaging chatbot handler..."
	cd backend/lambda_functions/chatbot_handler && \
		pip install -r requirements.txt -t package/ && \
		cp handler.py package/ && \
		cd package && zip -r ../chatbot_handler.zip .
	@echo "Packaging auth handler..."
	cd backend/lambda_functions/auth_handler && \
		pip install -r requirements.txt -t package/ && \
		cp handler.py package/ && \
		cd package && zip -r ../auth_handler.zip .
	@echo "Packaging monitoring handler..."
	cd backend/lambda_functions/monitoring_handler && \
		pip install -r requirements.txt -t package/ && \
		cp handler.py package/ && \
		cd package && zip -r ../monitoring_handler.zip .

# Infrastructure deployment
deploy-infra: ## Deploy infrastructure with Terraform
	@echo "Initializing Terraform..."
	cd infra/terraform && terraform init
	@echo "Planning Terraform deployment..."
	cd infra/terraform && terraform plan -out=tfplan
	@echo "Applying Terraform configuration..."
	cd infra/terraform && terraform apply tfplan
	@echo "Infrastructure deployed successfully!"

destroy-infra: ## Destroy infrastructure
	@echo "Destroying infrastructure..."
	cd infra/terraform && terraform destroy -auto-approve

# Application deployment
deploy-app: ## Deploy application code
	@echo "Deploying Lambda functions..."
	$(MAKE) deploy-lambdas
	@echo "Deploying Lex bot..."
	python pipeline/scripts/deploy_lex.py
	@echo "Deploying frontend..."
	cd frontend && npm run deploy

deploy-lambdas: package-lambdas ## Deploy Lambda functions
	@echo "Uploading Lambda packages..."
	python pipeline/scripts/package_lambda.py

# Development
dev: ## Start local development environment
	@echo "Starting local development servers..."
	@echo "Starting backend API..."
	cd backend && uvicorn main:app --reload --port 8000 &
	@echo "Starting frontend..."
	cd frontend && npm start &
	@echo "Development environment started!"

dev-stop: ## Stop local development environment
	@echo "Stopping development servers..."
	pkill -f "uvicorn main:app"
	pkill -f "npm start"

# Monitoring and operations
logs: ## View CloudWatch logs
	@echo "Fetching recent logs..."
	aws logs describe-log-groups --log-group-name-prefix "/aws/lambda/$(PROJECT_NAME)"
	aws logs tail "/aws/lambda/$(PROJECT_NAME)-chatbot" --follow

monitor: ## Open CloudWatch dashboard
	@echo "Opening monitoring dashboard..."
	aws cloudwatch get-dashboard --dashboard-name "$(PROJECT_NAME)-dashboard"

metrics: ## Show key metrics
	@echo "Fetching key metrics..."
	aws cloudwatch get-metric-statistics \
		--namespace "AWS/Lambda" \
		--metric-name "Duration" \
		--dimensions Name=FunctionName,Value=$(PROJECT_NAME)-chatbot \
		--start-time $(shell date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
		--end-time $(shell date -u +%Y-%m-%dT%H:%M:%S) \
		--period 300 \
		--statistics Average

# Security
security-scan: ## Run security scans
	@echo "Running security scans..."
	bandit -r backend/ -f json -o security-report.json
	@echo "Checking for secrets..."
	detect-secrets scan --baseline .secrets.baseline

rotate-secrets: ## Rotate secrets
	@echo "Rotating secrets..."
	python pipeline/scripts/rotate_secrets.py

# Utilities
validate: ## Validate all configurations
	@echo "Validating Terraform..."
	cd infra/terraform && terraform validate
	@echo "Validating CloudFormation templates..."
	aws cloudformation validate-template --template-body file://infra/cfn/template.yaml
	@echo "Validating buildspec files..."
	aws codebuild validate-project --source buildspec.yml

docs: ## Generate documentation
	@echo "Generating documentation..."
	cd docs && sphinx-build -b html . _build/html
	@echo "Documentation generated in docs/_build/html/"

# CI/CD
ci-test: ## Run CI tests
	$(MAKE) lint
	$(MAKE) test
	$(MAKE) security-scan

ci-build: ## CI build process
	$(MAKE) clean
	$(MAKE) install
	$(MAKE) ci-test
	$(MAKE) build

ci-deploy: ## CI deployment process
	$(MAKE) deploy-infra
	$(MAKE) deploy-app

# Environment management
env-dev: ## Switch to development environment
	@echo "Switching to development environment..."
	@export ENVIRONMENT=dev

env-staging: ## Switch to staging environment
	@echo "Switching to staging environment..."
	@export ENVIRONMENT=staging

env-prod: ## Switch to production environment
	@echo "Switching to production environment..."
	@export ENVIRONMENT=prod

# Backup and restore
backup: ## Backup DynamoDB tables
	@echo "Creating DynamoDB backup..."
	aws dynamodb create-backup \
		--table-name $(PROJECT_NAME)-conversations-$(ENVIRONMENT) \
		--backup-name $(PROJECT_NAME)-backup-$(shell date +%Y%m%d-%H%M%S)

restore: ## Restore from backup (requires BACKUP_ARN)
	@echo "Restoring from backup..."
	@test -n "$(BACKUP_ARN)" || (echo "BACKUP_ARN is required" && exit 1)
	aws dynamodb restore-table-from-backup \
		--target-table-name $(PROJECT_NAME)-conversations-$(ENVIRONMENT)-restored \
		--backup-arn $(BACKUP_ARN)

# Cost optimization
cost-report: ## Generate cost report
	@echo "Generating cost report..."
	aws ce get-cost-and-usage \
		--time-period Start=$(shell date -d '30 days ago' +%Y-%m-%d),End=$(shell date +%Y-%m-%d) \
		--granularity MONTHLY \
		--metrics BlendedCost \
		--group-by Type=DIMENSION,Key=SERVICE

# Health checks
health: ## Check system health
	@echo "Checking system health..."
	@echo "Lambda functions:"
	aws lambda list-functions --query 'Functions[?starts_with(FunctionName, `$(PROJECT_NAME)`)].{Name:FunctionName,State:State,Runtime:Runtime}'
	@echo "API Gateway:"
	aws apigateway get-rest-apis --query 'items[?name==`$(PROJECT_NAME)-api`].{Name:name,Id:id,Status:endpointConfiguration.types[0]}'
	@echo "DynamoDB tables:"
	aws dynamodb list-tables --query 'TableNames[?starts_with(@, `$(PROJECT_NAME)`)]'
