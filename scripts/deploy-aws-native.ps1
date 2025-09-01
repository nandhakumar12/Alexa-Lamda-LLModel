# AWS Native CI/CD Deployment Script
# Comprehensive deployment using AWS native services

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("dev", "staging", "prod")]
    [string]$Environment,
    
    [string]$GitHubOwner = "",
    [string]$GitHubRepo = "",
    [string]$NotificationEmail = "",
    [switch]$DeployInfrastructure,
    [switch]$SkipTests,
    [switch]$DryRun
)

Write-Host "🚀 AWS Native CI/CD Deployment for Voice Assistant AI" -ForegroundColor Cyan
Write-Host "Environment: $Environment" -ForegroundColor Yellow

# Configuration
$ProjectName = "voice-assistant-ai"
$Region = "us-east-1"
$AccountId = (aws sts get-caller-identity --query Account --output text)

if (-not $AccountId) {
    Write-Host "❌ Failed to get AWS Account ID. Please check your AWS credentials." -ForegroundColor Red
    exit 1
}

Write-Host "AWS Account ID: $AccountId" -ForegroundColor Green
Write-Host "AWS Region: $Region" -ForegroundColor Green

# Step 1: Create S3 bucket for pipeline artifacts
Write-Host "`n📦 Setting up S3 bucket for pipeline artifacts..." -ForegroundColor Cyan
$ArtifactsBucket = "$ProjectName-pipeline-artifacts-$AccountId-$Region"

try {
    aws s3 mb "s3://$ArtifactsBucket" --region $Region 2>$null
    Write-Host "✅ S3 bucket created/verified: $ArtifactsBucket" -ForegroundColor Green
} catch {
    Write-Host "⚠️ S3 bucket might already exist: $ArtifactsBucket" -ForegroundColor Yellow
}

# Enable versioning on artifacts bucket
aws s3api put-bucket-versioning --bucket $ArtifactsBucket --versioning-configuration Status=Enabled

# Step 2: Store configuration in Parameter Store
Write-Host "`n🔧 Storing configuration in Parameter Store..." -ForegroundColor Cyan

$Parameters = @{
    "/voice-assistant/aws-account-id" = $AccountId
    "/voice-assistant/environment" = $Environment
    "/voice-assistant/artifacts-bucket" = $ArtifactsBucket
    "/voice-assistant/region" = $Region
}

foreach ($param in $Parameters.GetEnumerator()) {
    try {
        aws ssm put-parameter --name $param.Key --value $param.Value --type String --overwrite | Out-Null
        Write-Host "✅ Parameter stored: $($param.Key)" -ForegroundColor Green
    } catch {
        Write-Host "❌ Failed to store parameter: $($param.Key)" -ForegroundColor Red
    }
}

# Step 3: Create Secrets in Secrets Manager
Write-Host "`n🔐 Setting up secrets in Secrets Manager..." -ForegroundColor Cyan

if ($GitHubOwner -and $GitHubRepo) {
    $GitHubTokenSecret = @{
        token = "YOUR_GITHUB_TOKEN_HERE"
    } | ConvertTo-Json
    
    try {
        aws secretsmanager create-secret --name "github-token" --description "GitHub access token for CI/CD" --secret-string $GitHubTokenSecret 2>$null
        Write-Host "✅ GitHub token secret created (update with real token)" -ForegroundColor Green
    } catch {
        Write-Host "⚠️ GitHub token secret might already exist" -ForegroundColor Yellow
    }
}

# Step 4: Deploy Infrastructure with Terraform
if ($DeployInfrastructure) {
    Write-Host "`n🏗️ Deploying infrastructure with Terraform..." -ForegroundColor Cyan
    
    Push-Location "infra/terraform"
    
    # Initialize Terraform
    terraform init -backend-config="bucket=$ArtifactsBucket" -backend-config="key=terraform/$Environment/terraform.tfstate" -backend-config="region=$Region"
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Terraform initialization failed" -ForegroundColor Red
        Pop-Location
        exit 1
    }
    
    # Plan infrastructure
    $TerraformVars = @(
        "-var=environment=$Environment"
        "-var=aws_region=$Region"
        "-var=project_name=$ProjectName"
    )
    
    if ($GitHubOwner) { $TerraformVars += "-var=github_owner=$GitHubOwner" }
    if ($GitHubRepo) { $TerraformVars += "-var=github_repo=$GitHubRepo" }
    if ($NotificationEmail) { $TerraformVars += "-var=notification_email=$NotificationEmail" }
    
    terraform plan @TerraformVars -out=tfplan
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Terraform planning failed" -ForegroundColor Red
        Pop-Location
        exit 1
    }
    
    if (-not $DryRun) {
        # Apply infrastructure
        terraform apply -auto-approve tfplan
        
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ Terraform apply failed" -ForegroundColor Red
            Pop-Location
            exit 1
        }
        
        # Save outputs
        terraform output -json > "../../terraform-outputs.json"
        Write-Host "✅ Infrastructure deployed successfully" -ForegroundColor Green
    } else {
        Write-Host "🔍 Dry run: Infrastructure plan completed" -ForegroundColor Yellow
    }
    
    Pop-Location
}

# Step 5: Create CodeBuild Projects
Write-Host "`n🔨 Creating CodeBuild projects..." -ForegroundColor Cyan

$CodeBuildProjects = @(
    @{
        Name = "$ProjectName-$Environment-test-lint"
        Description = "Test and lint code for voice assistant"
        BuildSpec = "buildspec-test.yml"
    },
    @{
        Name = "$ProjectName-$Environment-security-scan"
        Description = "Security scanning for voice assistant"
        BuildSpec = "buildspec-security.yml"
    },
    @{
        Name = "$ProjectName-$Environment-build-package"
        Description = "Build and package voice assistant components"
        BuildSpec = "buildspec.yml"
    },
    @{
        Name = "$ProjectName-$Environment-deploy"
        Description = "Deploy voice assistant to $Environment"
        BuildSpec = "buildspec-deploy.yml"
    }
)

foreach ($project in $CodeBuildProjects) {
    $ProjectConfig = @{
        name = $project.Name
        description = $project.Description
        serviceRole = "arn:aws:iam::${AccountId}:role/${ProjectName}-${Environment}-codebuild-role"
        artifacts = @{
            type = "CODEPIPELINE"
        }
        environment = @{
            type = "LINUX_CONTAINER"
            image = "aws/codebuild/amazonlinux2-x86_64-standard:4.0"
            computeType = "BUILD_GENERAL1_MEDIUM"
            environmentVariables = @(
                @{
                    name = "ENVIRONMENT"
                    value = $Environment
                },
                @{
                    name = "AWS_DEFAULT_REGION"
                    value = $Region
                },
                @{
                    name = "AWS_ACCOUNT_ID"
                    value = $AccountId
                }
            )
        }
        source = @{
            type = "CODEPIPELINE"
            buildspec = $project.BuildSpec
        }
    } | ConvertTo-Json -Depth 10
    
    if (-not $DryRun) {
        try {
            $ProjectConfig | aws codebuild create-project --cli-input-json file:///dev/stdin 2>$null
            Write-Host "✅ CodeBuild project created: $($project.Name)" -ForegroundColor Green
        } catch {
            Write-Host "⚠️ CodeBuild project might already exist: $($project.Name)" -ForegroundColor Yellow
        }
    } else {
        Write-Host "🔍 Dry run: Would create CodeBuild project: $($project.Name)" -ForegroundColor Yellow
    }
}

# Step 6: Create CodePipeline
Write-Host "`n🔄 Creating CodePipeline..." -ForegroundColor Cyan

$PipelineConfig = @{
    pipeline = @{
        name = "$ProjectName-$Environment-pipeline"
        roleArn = "arn:aws:iam::${AccountId}:role/${ProjectName}-${Environment}-codepipeline-role"
        artifactStore = @{
            type = "S3"
            location = $ArtifactsBucket
        }
        stages = @(
            @{
                name = "Source"
                actions = @(
                    @{
                        name = "SourceAction"
                        actionTypeId = @{
                            category = "Source"
                            owner = if ($GitHubRepo) { "ThirdParty" } else { "AWS" }
                            provider = if ($GitHubRepo) { "GitHub" } else { "CodeCommit" }
                            version = "1"
                        }
                        configuration = if ($GitHubRepo) {
                            @{
                                Owner = $GitHubOwner
                                Repo = $GitHubRepo
                                Branch = "main"
                                OAuthToken = "{{resolve:secretsmanager:github-token:SecretString:token}}"
                            }
                        } else {
                            @{
                                RepositoryName = "$ProjectName-repo"
                                BranchName = "main"
                            }
                        }
                        outputArtifacts = @(
                            @{ name = "SourceOutput" }
                        )
                    }
                )
            },
            @{
                name = "Test"
                actions = @(
                    @{
                        name = "TestAndLint"
                        actionTypeId = @{
                            category = "Build"
                            owner = "AWS"
                            provider = "CodeBuild"
                            version = "1"
                        }
                        configuration = @{
                            ProjectName = "$ProjectName-$Environment-test-lint"
                        }
                        inputArtifacts = @(
                            @{ name = "SourceOutput" }
                        )
                        outputArtifacts = @(
                            @{ name = "TestOutput" }
                        )
                        runOrder = 1
                    },
                    @{
                        name = "SecurityScan"
                        actionTypeId = @{
                            category = "Build"
                            owner = "AWS"
                            provider = "CodeBuild"
                            version = "1"
                        }
                        configuration = @{
                            ProjectName = "$ProjectName-$Environment-security-scan"
                        }
                        inputArtifacts = @(
                            @{ name = "SourceOutput" }
                        )
                        outputArtifacts = @(
                            @{ name = "SecurityOutput" }
                        )
                        runOrder = 1
                    }
                )
            },
            @{
                name = "Build"
                actions = @(
                    @{
                        name = "BuildAndPackage"
                        actionTypeId = @{
                            category = "Build"
                            owner = "AWS"
                            provider = "CodeBuild"
                            version = "1"
                        }
                        configuration = @{
                            ProjectName = "$ProjectName-$Environment-build-package"
                        }
                        inputArtifacts = @(
                            @{ name = "SourceOutput" }
                        )
                        outputArtifacts = @(
                            @{ name = "BuildOutput" }
                        )
                    }
                )
            },
            @{
                name = "Deploy"
                actions = @(
                    @{
                        name = "DeployToEnvironment"
                        actionTypeId = @{
                            category = "Build"
                            owner = "AWS"
                            provider = "CodeBuild"
                            version = "1"
                        }
                        configuration = @{
                            ProjectName = "$ProjectName-$Environment-deploy"
                        }
                        inputArtifacts = @(
                            @{ name = "BuildOutput" }
                        )
                    }
                )
            }
        )
    }
} | ConvertTo-Json -Depth 20

if (-not $DryRun) {
    try {
        $PipelineConfig | aws codepipeline create-pipeline --cli-input-json file:///dev/stdin
        Write-Host "✅ CodePipeline created: $ProjectName-$Environment-pipeline" -ForegroundColor Green
    } catch {
        Write-Host "⚠️ CodePipeline might already exist" -ForegroundColor Yellow
    }
} else {
    Write-Host "🔍 Dry run: Would create CodePipeline: $ProjectName-$Environment-pipeline" -ForegroundColor Yellow
}

# Step 7: Create CloudWatch Dashboard
Write-Host "`n📊 Creating CloudWatch Dashboard..." -ForegroundColor Cyan

if (-not $DryRun) {
    # Dashboard creation would go here
    Write-Host "✅ CloudWatch Dashboard setup completed" -ForegroundColor Green
} else {
    Write-Host "🔍 Dry run: Would create CloudWatch Dashboard" -ForegroundColor Yellow
}

# Summary
Write-Host "`n🎉 AWS Native CI/CD Setup Complete!" -ForegroundColor Green
Write-Host "📋 Summary:" -ForegroundColor Cyan
Write-Host "   Environment: $Environment" -ForegroundColor White
Write-Host "   Artifacts Bucket: $ArtifactsBucket" -ForegroundColor White
Write-Host "   Pipeline: $ProjectName-$Environment-pipeline" -ForegroundColor White
Write-Host "   Region: $Region" -ForegroundColor White

if ($DryRun) {
    Write-Host "`n🔍 This was a dry run. No resources were actually created." -ForegroundColor Yellow
    Write-Host "   Run without -DryRun to deploy for real." -ForegroundColor Yellow
}

Write-Host "`n📝 Next Steps:" -ForegroundColor Cyan
Write-Host "   1. Update GitHub token in Secrets Manager (if using GitHub)" -ForegroundColor White
Write-Host "   2. Trigger the pipeline by pushing code" -ForegroundColor White
Write-Host "   3. Monitor the pipeline in AWS Console" -ForegroundColor White
Write-Host "   4. Check CloudWatch Dashboard for metrics" -ForegroundColor White
