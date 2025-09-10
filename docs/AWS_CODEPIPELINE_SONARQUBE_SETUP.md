# AWS CodePipeline SonarQube Integration Guide

## 🎯 Overview

This guide provides step-by-step instructions for setting up SonarQube integration with your existing AWS CodePipeline for the Voice Assistant AI project.

## 📋 Prerequisites

- AWS CLI configured with appropriate permissions
- Terraform installed
- SonarQube account (SonarCloud or self-hosted)
- Access to your GitHub repository

## 🚀 Step-by-Step Setup

### Step 1: Get SonarQube Token

1. **For SonarCloud (Recommended)**:
   - Go to [SonarCloud.io](https://sonarcloud.io)
   - Sign up/Login with GitHub
   - Go to Account > Security
   - Generate a new token
   - Copy the token

2. **For Self-hosted SonarQube**:
   - Access your SonarQube instance
   - Go to User > My Account > Security
   - Generate a new token
   - Copy the token

### Step 2: Store Token in AWS Secrets Manager

#### Windows PowerShell:
```powershell
# Store the token
.\scripts\setup-sonar-secrets.ps1 -SonarToken "your_sonar_token_here"

# Verify the token was stored
aws secretsmanager get-secret-value --secret-id "voice-assistant-ai/sonar-token" --region us-east-1
```

#### Linux/macOS:
```bash
# Store the token
./scripts/setup-sonar-secrets.sh --token "your_sonar_token_here"

# Verify the token was stored
aws secretsmanager get-secret-value --secret-id "voice-assistant-ai/sonar-token" --region us-east-1
```

### Step 3: Configure Terraform Variables

Create or update `infra/terraform/terraform.tfvars`:

```hcl
# SonarQube Configuration
enable_sonarqube = true
sonar_host_url = "https://sonarcloud.io"  # or your self-hosted URL
sonar_organization = "your-organization-key"
sonar_token = "voice-assistant-ai/sonar-token"  # Secret name in Secrets Manager

# Other existing variables
name_prefix = "voice-ai"
environment = "production"
region = "us-east-1"
```

### Step 4: Deploy Infrastructure

```bash
cd infra/terraform

# Initialize Terraform
terraform init

# Plan the deployment
terraform plan

# Apply the changes
terraform apply
```

### Step 5: Verify Pipeline Configuration

1. **Check CodePipeline**:
   ```bash
   aws codepipeline get-pipeline --name voice-ai-pipeline
   ```

2. **Check CodeBuild Projects**:
   ```bash
   aws codebuild list-projects --query 'projects[?contains(@, `sonarqube`)]'
   ```

3. **Monitor Pipeline Execution**:
   ```bash
   aws codepipeline get-pipeline-state --name voice-ai-pipeline
   ```

## 🔧 Configuration Options

### Terraform Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `enable_sonarqube` | Enable SonarQube analysis | `true` | No |
| `sonar_host_url` | SonarQube server URL | `https://sonarcloud.io` | No |
| `sonar_organization` | SonarQube organization key | `voice-assistant-ai-org` | No |
| `sonar_token` | Secret name in Secrets Manager | `voice-assistant-ai/sonar-token` | No |

### Buildspec Configuration

The `buildspec-sonar.yml` file is automatically used by the SonarQube CodeBuild project:

```yaml
version: 0.2

phases:
  install:
    runtime-versions:
      python: 3.9
      nodejs: 16
    commands:
      - echo "Installing SonarQube Scanner and dependencies..."
      - pip install --upgrade pip
      - pip install bandit safety pytest pytest-cov
      - npm install -g sonarqube-scanner
      # ... rest of configuration
```

## 📊 Pipeline Flow

### Before SonarQube Integration
```
Source → Test → Security → Build → DeployDev → DeployStaging → DeployProd
```

### After SonarQube Integration
```
Source → Test → Security → SonarQubeAnalysis → Build → DeployDev → DeployStaging → DeployProd
```

### Parallel Execution
The Test and Security stages run in parallel, followed by SonarQube analysis:

```
Source
  ↓
Test ──┐
       ├─→ SonarQubeAnalysis → Build → Deploy...
Security ─┘
```

## 🎛️ Quality Gate Configuration

### Default Quality Gate
- **Coverage**: > 80%
- **Duplicated Lines**: < 3%
- **Maintainability Rating**: A
- **Reliability Rating**: A
- **Security Rating**: A

### Custom Quality Gate
1. Go to your SonarQube instance
2. Navigate to Administration > Quality Gates
3. Create a new quality gate
4. Configure thresholds
5. Set as default for your project

## 🔍 Monitoring and Troubleshooting

### View Pipeline Status
```bash
# Get pipeline execution history
aws codepipeline list-pipeline-executions --pipeline-name voice-ai-pipeline

# Get current pipeline state
aws codepipeline get-pipeline-state --name voice-ai-pipeline

# Get specific execution details
aws codepipeline get-pipeline-execution --pipeline-name voice-ai-pipeline --pipeline-execution-id <execution-id>
```

### View CodeBuild Logs
```bash
# List recent builds
aws codebuild list-builds-for-project --project-name voice-ai-sonarqube-analysis

# Get build details
aws codebuild batch-get-builds --ids <build-id>

# View logs (if build is running)
aws logs tail /aws/codebuild/voice-ai-sonarqube-analysis --follow
```

### Common Issues

#### 1. SonarQube Token Issues
```bash
# Verify token is stored correctly
aws secretsmanager get-secret-value --secret-id voice-assistant-ai/sonar-token

# Check if CodeBuild can access the secret
aws iam get-role-policy --role-name voice-ai-codebuild-role --policy-name voice-ai-codebuild-policy
```

#### 2. Build Failures
```bash
# Check build logs
aws logs get-log-events --log-group-name /aws/codebuild/voice-ai-sonarqube-analysis --log-stream-name <stream-name>
```

#### 3. Coverage Reports Missing
- Ensure test commands generate coverage reports
- Check if coverage files are in the correct location
- Verify file permissions

## 🔐 Security Considerations

### IAM Permissions
The CodeBuild role has the following permissions:
- `secretsmanager:GetSecretValue` - Access SonarQube token
- `secretsmanager:DescribeSecret` - Verify secret exists
- Standard CodeBuild permissions for S3, CloudWatch, etc.

### Token Security
- Token is stored in AWS Secrets Manager
- Encrypted at rest using AWS KMS
- Access is restricted to CodeBuild role
- Token is not logged or exposed in build logs

### Network Security
- SonarQube communication uses HTTPS
- No inbound firewall rules required
- Outbound HTTPS traffic to SonarQube servers

## 📈 Cost Optimization

### CodeBuild Costs
- **Compute Type**: `BUILD_GENERAL1_MEDIUM` (2 vCPU, 4 GB RAM)
- **Build Time**: Typically 5-10 minutes
- **Frequency**: On every code push
- **Estimated Cost**: ~$0.01-0.02 per build

### Secrets Manager Costs
- **Secret Storage**: $0.40 per secret per month
- **API Calls**: $0.05 per 10,000 requests
- **Estimated Cost**: ~$0.40-0.50 per month

### SonarCloud Costs
- **Free Tier**: Up to 100,000 lines of code
- **Paid Plans**: Starting at $10/month for additional lines
- **Check**: [SonarCloud Pricing](https://sonarcloud.io/pricing)

## 🚀 Advanced Configuration

### Custom Quality Gates
```hcl
# In terraform.tfvars
sonar_quality_gate = "custom-gate-name"
```

### Multiple Environments
```hcl
# Different SonarQube projects per environment
sonar_project_key = "voice-assistant-ai-${var.environment}"
```

### Custom Buildspec
```hcl
# Use custom buildspec file
buildspec_file = "custom-buildspec-sonar.yml"
```

## 📚 Additional Resources

- [AWS CodePipeline Documentation](https://docs.aws.amazon.com/codepipeline/)
- [AWS CodeBuild Documentation](https://docs.aws.amazon.com/codebuild/)
- [SonarQube Scanner Documentation](https://docs.sonarqube.org/latest/analysis/scan/sonarscanner/)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)

## 🤝 Support

For issues specific to this integration:
1. Check the troubleshooting section above
2. Review AWS CloudWatch logs
3. Check SonarQube project dashboard
4. Contact the development team

---

**Happy Coding! 🚀**
