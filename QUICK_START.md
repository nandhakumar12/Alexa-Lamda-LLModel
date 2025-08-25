# 🚀 Voice Assistant AI - Quick Start Guide

Get your Voice Assistant AI up and running in **30 minutes**!

## ⚡ Prerequisites (5 minutes)

### 1. Install Required Tools
```bash
# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Install Terraform
wget https://releases.hashicorp.com/terraform/1.6.0/terraform_1.6.0_linux_amd64.zip
unzip terraform_1.6.0_linux_amd64.zip
sudo mv terraform /usr/local/bin/

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verify installations
aws --version
terraform --version
node --version
python3 --version
```

### 2. Configure AWS
```bash
# Configure AWS CLI
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key  
# Default region: us-east-1
# Default output format: json

# Verify configuration
aws sts get-caller-identity
```

## 🏗️ Deploy Infrastructure (10 minutes)

### 1. Clone and Setup
```bash
git clone https://github.com/your-org/voice-assistant-ai.git
cd voice-assistant-ai

# Copy configuration template
cp infra/terraform/terraform.tfvars.example infra/terraform/terraform.tfvars

# Edit with your email for alerts
sed -i 's/admin@yourcompany.com/your-email@company.com/g' infra/terraform/terraform.tfvars
```

### 2. Deploy AWS Infrastructure
```bash
cd infra/terraform

# Initialize Terraform
terraform init

# Deploy (takes ~8 minutes)
terraform apply -auto-approve -var-file="terraform.tfvars"

# Save outputs for later use
terraform output > ../../deployment-outputs.txt
```

## 🤖 Configure Lex Bot (5 minutes)

### Option 1: Quick Setup (Automated)
```bash
cd ../../pipeline/scripts

# Get Lambda ARN
LAMBDA_ARN=$(aws lambda get-function --function-name voice-assistant-ai-chatbot-prod --query 'Configuration.FunctionArn' --output text)

# Deploy Lex bot
python deploy_lex.py \
  --bot-config ../../lex/bot-config.json \
  --locale-config ../../lex/locale-config.json \
  --intents-config ../../lex/intents.json \
  --environment prod \
  --lambda-arn $LAMBDA_ARN
```

### Option 2: Manual Setup (AWS Console)
1. Go to [Amazon Lex Console](https://console.aws.amazon.com/lexv2/)
2. Create bot: `voice-assistant-ai-prod-bot`
3. Add intents: `WelcomeIntent`, `HelpIntent`
4. Build bot and create alias: `prod`

## 🚀 Deploy Application (5 minutes)

### 1. Deploy Lambda Functions
```bash
cd ../../

# Package and deploy all Lambda functions
python pipeline/scripts/package_lambda.py --function-dir backend/lambda_functions/chatbot_handler --environment prod
python pipeline/scripts/package_lambda.py --function-dir backend/lambda_functions/auth_handler --environment prod
python pipeline/scripts/package_lambda.py --function-dir backend/lambda_functions/monitoring_handler --environment prod
```

### 2. Deploy Frontend
```bash
cd frontend

# Get infrastructure outputs
API_URL=$(cd ../infra/terraform && terraform output -raw api_gateway_url)
USER_POOL_ID=$(cd ../infra/terraform && terraform output -raw cognito_user_pool_id)
CLIENT_ID=$(cd ../infra/terraform && terraform output -raw cognito_user_pool_client_id)

# Create environment file
cat > .env.production << EOF
REACT_APP_API_GATEWAY_URL=$API_URL
REACT_APP_COGNITO_USER_POOL_ID=$USER_POOL_ID
REACT_APP_COGNITO_CLIENT_ID=$CLIENT_ID
REACT_APP_AWS_REGION=us-east-1
REACT_APP_ENVIRONMENT=prod
EOF

# Install and build
npm install
npm run build

# Deploy to S3
S3_BUCKET=$(cd ../infra/terraform && terraform output -raw s3_bucket_name)
aws s3 sync build/ s3://$S3_BUCKET --delete
```

## ✅ Test Your Deployment (5 minutes)

### 1. Test API
```bash
# Test health endpoint
API_URL=$(cd infra/terraform && terraform output -raw api_gateway_url)
curl "$API_URL/health"
# Expected: {"status":"healthy"}
```

### 2. Test Lambda Functions
```bash
# Test chatbot
aws lambda invoke --function-name voice-assistant-ai-chatbot-prod --payload '{"httpMethod":"GET","path":"/health"}' response.json
cat response.json

# Test auth
aws lambda invoke --function-name voice-assistant-ai-auth-prod --payload '{"httpMethod":"GET","path":"/health"}' auth-response.json
cat auth-response.json
```

### 3. Create Test User
```bash
# Create Cognito user
USER_POOL_ID=$(cd infra/terraform && terraform output -raw cognito_user_pool_id)

aws cognito-idp admin-create-user \
  --user-pool-id $USER_POOL_ID \
  --username testuser@example.com \
  --user-attributes Name=email,Value=testuser@example.com \
  --temporary-password TempPass123! \
  --message-action SUPPRESS

# Set permanent password
aws cognito-idp admin-set-user-password \
  --user-pool-id $USER_POOL_ID \
  --username testuser@example.com \
  --password TestPassword123! \
  --permanent
```

### 4. Access Your Application
```bash
# Get your application URL
echo "Your Voice Assistant is ready!"
echo "Web Interface: https://$(cd infra/terraform && terraform output -raw s3_bucket_name).s3-website-us-east-1.amazonaws.com"
echo "API Endpoint: $(cd infra/terraform && terraform output -raw api_gateway_url)"
echo ""
echo "Test Credentials:"
echo "Username: testuser@example.com"
echo "Password: TestPassword123!"
```

## 🎉 You're Done!

Your Voice Assistant AI is now live and ready to use!

### What You Can Do Now:
- 🌐 **Access the web interface** and start chatting
- 🎤 **Test voice commands** using your microphone
- 👤 **Login with your test user** credentials
- 📊 **Monitor performance** in CloudWatch
- 🔧 **Customize the bot** by adding more intents

### Next Steps:
1. **Customize Lex Bot**: Add more intents and responses
2. **Setup Alexa Skill**: Connect to Alexa Skills Kit
3. **Add Monitoring**: Setup CloudWatch alerts
4. **Scale Up**: Configure auto-scaling for production

## 🆘 Need Help?

If something goes wrong:

1. **Check the logs**:
   ```bash
   aws logs tail /aws/lambda/voice-assistant-ai-chatbot-prod --follow
   ```

2. **Verify resources**:
   ```bash
   aws lambda list-functions --query 'Functions[?starts_with(FunctionName, `voice-assistant-ai`)]'
   ```

3. **Clean up and retry**:
   ```bash
   cd infra/terraform
   terraform destroy -auto-approve
   # Then start over from step 1
   ```

4. **Get support**: Check the main [README.md](README.md) for detailed troubleshooting

**Happy building! 🚀**
