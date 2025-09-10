#!/bin/bash

# Quick Start SonarQube Script
# This script provides a fast way to get SonarQube running locally

set -e

echo "🚀 Quick Start SonarQube for Voice Assistant AI"
echo "=============================================="
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Start SonarQube
echo "📦 Starting SonarQube..."
docker-compose -f docker-compose.sonar.yml up -d

echo "⏳ Waiting for SonarQube to be ready..."
echo "This may take 2-3 minutes on first run..."

# Wait for SonarQube to be ready
max_attempts=30
attempt=1

while [ $attempt -le $max_attempts ]; do
    if curl -s http://localhost:9000/api/system/status > /dev/null 2>&1; then
        echo "✅ SonarQube is ready!"
        break
    fi
    
    echo "⏳ Attempt $attempt/$max_attempts - Still starting..."
    sleep 10
    ((attempt++))
done

if [ $attempt -gt $max_attempts ]; then
    echo "❌ SonarQube failed to start within 5 minutes"
    echo "Check logs with: docker-compose -f docker-compose.sonar.yml logs"
    exit 1
fi

echo ""
echo "🎉 SonarQube is now running!"
echo ""
echo "📋 Next Steps:"
echo "1. Open http://localhost:9000 in your browser"
echo "2. Login with admin/admin"
echo "3. Change the default password"
echo "4. Generate a token: User > My Account > Security"
echo "5. Set the token: export SONAR_TOKEN=your_token_here"
echo "6. Run analysis: make sonar-analyze"
echo ""
echo "🔧 Useful Commands:"
echo "- Stop SonarQube: make sonar-stop"
echo "- View logs: docker-compose -f docker-compose.sonar.yml logs -f"
echo "- Run analysis: make sonar-analyze"
echo "- Clean data: make sonar-clean"
echo ""
echo "📚 For detailed setup, see: docs/SONARQUBE_SETUP.md"
