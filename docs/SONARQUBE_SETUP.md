# SonarQube Setup Guide for Voice Assistant AI

## 🎯 Overview

This guide provides comprehensive instructions for setting up SonarQube code quality analysis in the Voice Assistant AI project. SonarQube will analyze both the React/TypeScript frontend and Python backend code.

## 📋 Prerequisites

- Docker and Docker Compose
- Node.js 16+
- Python 3.9+
- Git

## 🚀 Quick Start

### 1. Local Development Setup

```bash
# Make the setup script executable
chmod +x scripts/setup-sonarqube.sh

# Run the setup script
./scripts/setup-sonarqube.sh
```

### 2. Manual Setup

#### Step 1: Start SonarQube

```bash
# Start SonarQube with Docker Compose
docker-compose -f docker-compose.sonar.yml up -d

# Wait for SonarQube to be ready (takes 2-3 minutes)
curl -s http://localhost:9000/api/system/status
```

#### Step 2: Access SonarQube

- Open http://localhost:9000 in your browser
- Login with `admin/admin`
- Change the default password

#### Step 3: Generate Token

1. Go to User > My Account > Security
2. Generate a new token
3. Copy the token and set it as environment variable:

```bash
export SONAR_TOKEN=your_token_here
```

#### Step 4: Run Analysis

```bash
# Install SonarQube Scanner
npm install -g sonarqube-scanner

# Run analysis
sonar-scanner
```

## 🔧 Configuration Files

### sonar-project.properties

Main configuration file that defines:
- Project identification
- Source code paths
- Test paths
- Coverage report paths
- Exclusions
- Quality gate settings

### buildspec-sonar.yml

Dedicated buildspec for SonarQube analysis in AWS CodeBuild:
- Installs required dependencies
- Generates coverage reports
- Runs SonarQube analysis
- Handles both Python and JavaScript/TypeScript

### docker-compose.sonar.yml

Docker Compose configuration for local SonarQube:
- SonarQube Community Edition
- PostgreSQL database
- SonarQube Scanner CLI
- Persistent data volumes

## 🏗️ CI/CD Integration

### AWS CodePipeline Integration

The existing buildspec files have been updated to include SonarQube analysis:

1. **buildspec.yml** - Main build with optional SonarQube analysis
2. **buildspec-test.yml** - Testing with coverage generation
3. **buildspec-sonar.yml** - Dedicated SonarQube analysis

### Environment Variables

Set these in your CodeBuild project:

```bash
SONAR_HOST_URL=https://your-sonarqube-instance.com
SONAR_TOKEN=your_sonarqube_token
SONAR_ORGANIZATION=voice-assistant-ai-org
```

### GitHub Actions Integration

The `.github/workflows/sonarqube.yml` file provides:
- Automatic analysis on push/PR
- Coverage report generation
- Artifact upload
- Quality gate enforcement

## 📊 Analysis Coverage

### Frontend (React/TypeScript)
- **Source**: `frontend/src/`
- **Tests**: `frontend/src/__tests__/`
- **Coverage**: Jest coverage reports
- **Linting**: ESLint integration
- **Exclusions**: `node_modules/`, `build/`, `dist/`

### Backend (Python)
- **Source**: `backend/lambda_functions/`, `backend/shared/`
- **Tests**: `backend/lambda_functions/tests/`
- **Coverage**: pytest coverage reports
- **Linting**: Black, Flake8 integration
- **Security**: Bandit, Safety scans
- **Exclusions**: `__pycache__/`, `*.pyc`, `venv/`

### Infrastructure (Terraform)
- **Source**: `infra/terraform/`
- **Exclusions**: `.terraform/`, `terraform.tfstate*`

## 🎛️ Quality Gates

### Default Quality Gate
- **Coverage**: > 80%
- **Duplicated Lines**: < 3%
- **Maintainability Rating**: A
- **Reliability Rating**: A
- **Security Rating**: A
- **Security Hotspots**: 0

### Custom Quality Gate
You can create custom quality gates in SonarQube:
1. Go to Administration > Quality Gates
2. Create new quality gate
3. Configure thresholds
4. Set as default

## 🔍 Code Analysis Rules

### Python Rules
- **Security**: Bandit security issues
- **Code Smells**: PEP 8 violations, complexity
- **Bugs**: Potential runtime errors
- **Coverage**: Test coverage analysis

### JavaScript/TypeScript Rules
- **Security**: ESLint security rules
- **Code Smells**: Code complexity, unused variables
- **Bugs**: Potential runtime errors
- **Coverage**: Jest coverage analysis

### Terraform Rules
- **Security**: Infrastructure security issues
- **Code Smells**: Resource naming, structure
- **Bugs**: Configuration errors

## 📈 Reports and Dashboards

### Project Dashboard
- **Overview**: Code quality metrics
- **Issues**: Bugs, vulnerabilities, code smells
- **Coverage**: Test coverage by component
- **Duplications**: Code duplication analysis
- **Security**: Security hotspots and vulnerabilities

### Quality Gate Status
- **Passed**: All quality gate conditions met
- **Failed**: One or more conditions not met
- **Warning**: Quality gate conditions not met but not blocking

## 🛠️ Troubleshooting

### Common Issues

#### SonarQube Not Starting
```bash
# Check Docker logs
docker-compose -f docker-compose.sonar.yml logs

# Check system resources
docker system df
```

#### Analysis Fails
```bash
# Check SonarQube Scanner logs
sonar-scanner -X

# Verify token permissions
curl -u $SONAR_TOKEN: http://localhost:9000/api/user_tokens/search
```

#### Coverage Reports Missing
```bash
# Generate coverage reports manually
cd backend/lambda_functions
python -m pytest . --cov=. --cov-report=xml
cd frontend
npm test -- --coverage
```

### Performance Optimization

#### Large Codebase
- Use exclusions to skip unnecessary files
- Configure analysis timeout
- Use incremental analysis

#### Memory Issues
- Increase Docker memory limits
- Use SonarQube Scanner with more memory
- Configure JVM heap size

## 🔐 Security Considerations

### Token Management
- Use project-specific tokens
- Rotate tokens regularly
- Store tokens securely (AWS Secrets Manager)

### Network Security
- Use HTTPS in production
- Configure firewall rules
- Use VPN for remote access

### Data Privacy
- Review exclusions for sensitive data
- Configure data retention policies
- Use on-premises deployment for sensitive projects

## 📚 Additional Resources

- [SonarQube Documentation](https://docs.sonarqube.org/)
- [SonarQube Scanner Documentation](https://docs.sonarqube.org/latest/analysis/scan/sonarscanner/)
- [Quality Gates Guide](https://docs.sonarqube.org/latest/user-guide/quality-gates/)
- [Code Coverage Guide](https://docs.sonarqube.org/latest/user-guide/code-coverage/)

## 🤝 Support

For issues specific to this project:
1. Check the troubleshooting section
2. Review SonarQube logs
3. Check GitHub Issues
4. Contact the development team

---

**Happy Coding! 🚀**
