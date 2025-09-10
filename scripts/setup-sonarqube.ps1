# SonarQube Setup Script for Voice Assistant AI Project (PowerShell)
# This script sets up SonarQube for local development and CI/CD integration

param(
    [switch]$SkipDockerCheck,
    [switch]$SkipAnalysis
)

Write-Host "🚀 Setting up SonarQube for Voice Assistant AI Project..." -ForegroundColor Blue

# Function to print colored output
function Write-Status {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Check if Docker is installed
function Test-Docker {
    if (-not $SkipDockerCheck) {
        try {
            $null = docker --version
            $null = docker-compose --version
            Write-Success "Docker and Docker Compose are installed"
        }
        catch {
            Write-Error "Docker is not installed. Please install Docker Desktop first."
            exit 1
        }
    }
}

# Check if Node.js is installed
function Test-NodeJS {
    try {
        $nodeVersion = node --version
        Write-Success "Node.js $nodeVersion is installed"
    }
    catch {
        Write-Error "Node.js is not installed. Please install Node.js 16+ first."
        exit 1
    }
}

# Check if Python is installed
function Test-Python {
    try {
        $pythonVersion = python --version
        Write-Success "Python $pythonVersion is installed"
    }
    catch {
        Write-Error "Python 3 is not installed. Please install Python 3.9+ first."
        exit 1
    }
}

# Install SonarQube Scanner
function Install-SonarScanner {
    Write-Status "Installing SonarQube Scanner..."
    
    try {
        $null = sonar-scanner --version
        Write-Success "SonarQube Scanner is already installed"
    }
    catch {
        Write-Status "Installing SonarQube Scanner via npm..."
        npm install -g sonarqube-scanner
        Write-Success "SonarQube Scanner installed successfully"
    }
}

# Start SonarQube with Docker Compose
function Start-SonarQube {
    Write-Status "Starting SonarQube with Docker Compose..."
    
    if (Test-Path "docker-compose.sonar.yml") {
        docker-compose -f docker-compose.sonar.yml up -d
        Write-Success "SonarQube started successfully"
        Write-Status "SonarQube is available at: http://localhost:9000"
        Write-Status "Default credentials: admin/admin"
        Write-Warning "Please change the default password on first login"
    }
    else {
        Write-Error "docker-compose.sonar.yml not found"
        exit 1
    }
}

# Wait for SonarQube to be ready
function Wait-ForSonarQube {
    Write-Status "Waiting for SonarQube to be ready..."
    
    $maxAttempts = 30
    $attempt = 1
    
    while ($attempt -le $maxAttempts) {
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:9000/api/system/status" -UseBasicParsing -TimeoutSec 5
            if ($response.StatusCode -eq 200) {
                Write-Success "SonarQube is ready!"
                return
            }
        }
        catch {
            # SonarQube not ready yet
        }
        
        Write-Status "Attempt $attempt/$maxAttempts - SonarQube not ready yet, waiting 10 seconds..."
        Start-Sleep -Seconds 10
        $attempt++
    }
    
    Write-Error "SonarQube failed to start within 5 minutes"
    exit 1
}

# Generate SonarQube token instructions
function Show-TokenInstructions {
    Write-Status "To generate a SonarQube token:"
    Write-Host "1. Open http://localhost:9000 in your browser"
    Write-Host "2. Login with admin/admin"
    Write-Host "3. Go to User > My Account > Security"
    Write-Host "4. Generate a new token"
    Write-Host "5. Copy the token and set it as SONAR_TOKEN environment variable"
    Write-Host ""
    Write-Host "Example: `$env:SONAR_TOKEN='your_token_here'"
    Write-Host ""
    Read-Host "Press Enter when you have generated the token"
}

# Run SonarQube analysis
function Start-Analysis {
    if ($SkipAnalysis) {
        Write-Status "Skipping analysis as requested"
        return
    }
    
    Write-Status "Running SonarQube analysis..."
    
    if (-not $env:SONAR_TOKEN) {
        Write-Warning "SONAR_TOKEN not set. Please set it first:"
        Write-Host "`$env:SONAR_TOKEN='your_token_here'"
        return
    }
    
    # Generate coverage reports first
    Write-Status "Generating coverage reports..."
    
    # Python coverage
    if (Test-Path "backend/lambda_functions") {
        Set-Location "backend/lambda_functions"
        python -m pytest . --cov=. --cov-report=xml --cov-report=html --cov-report=term
        if (-not (Test-Path "../../coverage")) {
            New-Item -ItemType Directory -Path "../../coverage" -Force
        }
        if (Test-Path "coverage.xml") {
            Copy-Item "coverage.xml" "../../coverage/"
        }
        Set-Location "../.."
    }
    
    # Frontend coverage
    if (Test-Path "frontend") {
        Set-Location "frontend"
        $env:CI = "true"
        npm test -- --coverage --watchAll=false --testTimeout=10000
        Set-Location ".."
    }
    
    # Run SonarQube analysis
    sonar-scanner `
        -Dsonar.projectKey=voice-assistant-ai `
        -Dsonar.host.url=http://localhost:9000 `
        -Dsonar.login=$env:SONAR_TOKEN `
        -Dsonar.organization=voice-assistant-ai-org `
        -Dsonar.python.coverage.reportPaths=coverage/coverage.xml `
        -Dsonar.javascript.lcov.reportPaths=frontend/coverage/lcov.info `
        -Dsonar.typescript.lcov.reportPaths=frontend/coverage/lcov.info `
        -Dsonar.sources=frontend/src,backend/lambda_functions,backend/shared,infra/terraform `
        -Dsonar.tests=frontend/src/__tests__,backend/lambda_functions/tests `
        -Dsonar.exclusions=**/node_modules/**,**/build/**,**/dist/**,**/coverage/**,**/terraform/.terraform/**,**/terraform/terraform.tfstate**,**/terraform/terraform.tfstate.backup**,**/*.min.js,**/*.bundle.js `
        -Dsonar.test.exclusions=**/node_modules/**,**/build/**,**/dist/**,**/coverage/**,**/terraform/.terraform/**,**/terraform/terraform.tfstate**,**/terraform/terraform.tfstate.backup** `
        -Dsonar.cpd.exclusions=**/node_modules/**,**/build/**,**/dist/**,**/coverage/**,**/terraform/.terraform/**,**/terraform/terraform.tfstate**,**/terraform/terraform.tfstate.backup** `
        -Dsonar.qualitygate.wait=true
    
    Write-Success "SonarQube analysis completed!"
    Write-Status "Check the results at: http://localhost:9000/dashboard?id=voice-assistant-ai"
}

# Main execution
function Main {
    Write-Host "🎯 Voice Assistant AI - SonarQube Setup" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    
    # Check prerequisites
    Test-Docker
    Test-NodeJS
    Test-Python
    
    # Install SonarQube Scanner
    Install-SonarScanner
    
    # Start SonarQube
    Start-SonarQube
    
    # Wait for SonarQube to be ready
    Wait-ForSonarQube
    
    # Generate token instructions
    Show-TokenInstructions
    
    # Run analysis
    Start-Analysis
    
    Write-Host ""
    Write-Success "SonarQube setup completed successfully!"
    Write-Host ""
    Write-Host "📋 Next Steps:"
    Write-Host "1. Access SonarQube at: http://localhost:9000"
    Write-Host "2. Review the analysis results"
    Write-Host "3. Configure quality gates as needed"
    Write-Host "4. Set up CI/CD integration with your pipeline"
    Write-Host ""
    Write-Host "🔧 Useful Commands:"
    Write-Host "- Stop SonarQube: docker-compose -f docker-compose.sonar.yml down"
    Write-Host "- View logs: docker-compose -f docker-compose.sonar.yml logs -f"
    Write-Host "- Run analysis: .\scripts\setup-sonarqube.ps1"
}

# Run main function
Main
