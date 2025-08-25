# Diagnose API Gateway issues
Write-Host "Diagnosing API Gateway Issues..." -ForegroundColor Cyan

$apiId = "7orgj957oe"
Write-Host "Checking API Gateway: $apiId" -ForegroundColor Yellow

# Check API Gateway resources
Write-Host "Getting API Gateway resources..." -ForegroundColor Yellow
$resources = aws apigateway get-resources --rest-api-id $apiId --output json 2>$null | ConvertFrom-Json

if ($resources -and $resources.items) {
    Write-Host "Found resources:" -ForegroundColor Green
    foreach ($resource in $resources.items) {
        Write-Host "  Path: $($resource.path) | ID: $($resource.id)" -ForegroundColor White
        
        # Check methods for each resource
        if ($resource.resourceMethods) {
            $methods = $resource.resourceMethods | Get-Member -MemberType NoteProperty | Select-Object -ExpandProperty Name
            Write-Host "    Methods: $($methods -join ', ')" -ForegroundColor Cyan
        }
    }
} else {
    Write-Host "No resources found or API Gateway not accessible" -ForegroundColor Red
}

# Check deployments
Write-Host "`nChecking deployments..." -ForegroundColor Yellow
$deployments = aws apigateway get-deployments --rest-api-id $apiId --output json 2>$null | ConvertFrom-Json

if ($deployments -and $deployments.items) {
    Write-Host "Found deployments:" -ForegroundColor Green
    foreach ($deployment in $deployments.items) {
        Write-Host "  ID: $($deployment.id) | Created: $($deployment.createdDate)" -ForegroundColor White
    }
} else {
    Write-Host "No deployments found" -ForegroundColor Red
}

# Check stages
Write-Host "`nChecking stages..." -ForegroundColor Yellow
$stages = aws apigateway get-stages --rest-api-id $apiId --output json 2>$null | ConvertFrom-Json

if ($stages -and $stages.item) {
    Write-Host "Found stages:" -ForegroundColor Green
    foreach ($stage in $stages.item) {
        Write-Host "  Stage: $($stage.stageName) | Deployment: $($stage.deploymentId)" -ForegroundColor White
    }
} else {
    Write-Host "No stages found" -ForegroundColor Red
}

Write-Host "`nDiagnosis complete!" -ForegroundColor Green
