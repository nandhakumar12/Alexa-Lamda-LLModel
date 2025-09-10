#!/bin/bash

# SonarQube Setup Script for Voice Assistant AI Project
# This script sets up SonarQube for local development and CI/CD integration

set -e

echo "🚀 Setting up SonarQube for Voice Assistant AI Project..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_success "Docker and Docker Compose are installed"
}

# Check if Node.js is installed
check_nodejs() {
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed. Please install Node.js 16+ first."
        exit 1
    fi
    
    NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
    if [ "$NODE_VERSION" -lt 16 ]; then
        print_error "Node.js version 16+ is required. Current version: $(node --version)"
        exit 1
    fi
    
    print_success "Node.js $(node --version) is installed"
}

# Check if Python is installed
check_python() {
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3.9+ first."
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    print_success "Python $PYTHON_VERSION is installed"
}

# Install SonarQube Scanner
install_sonar_scanner() {
    print_status "Installing SonarQube Scanner..."
    
    if command -v sonar-scanner &> /dev/null; then
        print_success "SonarQube Scanner is already installed"
        return
    fi
    
    # Install via npm
    npm install -g sonarqube-scanner
    
    print_success "SonarQube Scanner installed successfully"
}

# Start SonarQube with Docker Compose
start_sonarqube() {
    print_status "Starting SonarQube with Docker Compose..."
    
    if [ -f "docker-compose.sonar.yml" ]; then
        docker-compose -f docker-compose.sonar.yml up -d
        print_success "SonarQube started successfully"
        print_status "SonarQube is available at: http://localhost:9000"
        print_status "Default credentials: admin/admin"
        print_warning "Please change the default password on first login"
    else
        print_error "docker-compose.sonar.yml not found"
        exit 1
    fi
}

# Wait for SonarQube to be ready
wait_for_sonarqube() {
    print_status "Waiting for SonarQube to be ready..."
    
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s http://localhost:9000/api/system/status > /dev/null 2>&1; then
            print_success "SonarQube is ready!"
            return 0
        fi
        
        print_status "Attempt $attempt/$max_attempts - SonarQube not ready yet, waiting 10 seconds..."
        sleep 10
        ((attempt++))
    done
    
    print_error "SonarQube failed to start within 5 minutes"
    exit 1
}

# Generate SonarQube token
generate_token() {
    print_status "To generate a SonarQube token:"
    echo "1. Open http://localhost:9000 in your browser"
    echo "2. Login with admin/admin"
    echo "3. Go to User > My Account > Security"
    echo "4. Generate a new token"
    echo "5. Copy the token and set it as SONAR_TOKEN environment variable"
    echo ""
    echo "Example: export SONAR_TOKEN=your_token_here"
    echo ""
    read -p "Press Enter when you have generated the token..."
}

# Run SonarQube analysis
run_analysis() {
    print_status "Running SonarQube analysis..."
    
    if [ -z "$SONAR_TOKEN" ]; then
        print_warning "SONAR_TOKEN not set. Please set it first:"
        echo "export SONAR_TOKEN=your_token_here"
        return 1
    fi
    
    # Generate coverage reports first
    print_status "Generating coverage reports..."
    
    # Python coverage
    if [ -d "backend/lambda_functions" ]; then
        cd backend/lambda_functions
        python3 -m pytest . --cov=. --cov-report=xml --cov-report=html --cov-report=term || echo "Some tests failed"
        mkdir -p ../../coverage
        cp coverage.xml ../../coverage/ || echo "No coverage.xml generated"
        cd ../..
    fi
    
    # Frontend coverage
    if [ -d "frontend" ]; then
        cd frontend
        CI=true npm test -- --coverage --watchAll=false --testTimeout=10000 || echo "Some frontend tests failed"
        cd ..
    fi
    
    # Run SonarQube analysis
    sonar-scanner \
        -Dsonar.projectKey=voice-assistant-ai \
        -Dsonar.host.url=http://localhost:9000 \
        -Dsonar.login=$SONAR_TOKEN \
        -Dsonar.organization=voice-assistant-ai-org \
        -Dsonar.python.coverage.reportPaths=coverage/coverage.xml \
        -Dsonar.javascript.lcov.reportPaths=frontend/coverage/lcov.info \
        -Dsonar.typescript.lcov.reportPaths=frontend/coverage/lcov.info \
        -Dsonar.sources=frontend/src,backend/lambda_functions,backend/shared,infra/terraform \
        -Dsonar.tests=frontend/src/__tests__,backend/lambda_functions/tests \
        -Dsonar.exclusions=**/node_modules/**,**/build/**,**/dist/**,**/coverage/**,**/terraform/.terraform/**,**/terraform/terraform.tfstate**,**/terraform/terraform.tfstate.backup**,**/*.min.js,**/*.bundle.js \
        -Dsonar.test.exclusions=**/node_modules/**,**/build/**,**/dist/**,**/coverage/**,**/terraform/.terraform/**,**/terraform/terraform.tfstate**,**/terraform/terraform.tfstate.backup** \
        -Dsonar.cpd.exclusions=**/node_modules/**,**/build/**,**/dist/**,**/coverage/**,**/terraform/.terraform/**,**/terraform/terraform.tfstate**,**/terraform/terraform.tfstate.backup** \
        -Dsonar.qualitygate.wait=true
    
    print_success "SonarQube analysis completed!"
    print_status "Check the results at: http://localhost:9000/dashboard?id=voice-assistant-ai"
}

# Main execution
main() {
    echo "🎯 Voice Assistant AI - SonarQube Setup"
    echo "========================================"
    echo ""
    
    # Check prerequisites
    check_docker
    check_nodejs
    check_python
    
    # Install SonarQube Scanner
    install_sonar_scanner
    
    # Start SonarQube
    start_sonarqube
    
    # Wait for SonarQube to be ready
    wait_for_sonarqube
    
    # Generate token instructions
    generate_token
    
    # Run analysis
    run_analysis
    
    echo ""
    print_success "SonarQube setup completed successfully!"
    echo ""
    echo "📋 Next Steps:"
    echo "1. Access SonarQube at: http://localhost:9000"
    echo "2. Review the analysis results"
    echo "3. Configure quality gates as needed"
    echo "4. Set up CI/CD integration with your pipeline"
    echo ""
    echo "🔧 Useful Commands:"
    echo "- Stop SonarQube: docker-compose -f docker-compose.sonar.yml down"
    echo "- View logs: docker-compose -f docker-compose.sonar.yml logs -f"
    echo "- Run analysis: ./scripts/setup-sonarqube.sh"
}

# Run main function
main "$@"
