# Find and invalidate CloudFront distribution
Write-Host "Finding CloudFront distribution..." -ForegroundColor Yellow

# Get all distributions and find the one with our S3 bucket
$distributions = aws cloudfront list-distributions --output json 2>$null | ConvertFrom-Json

if ($distributions -and $distributions.DistributionList.Items) {
    foreach ($dist in $distributions.DistributionList.Items) {
        $origins = $dist.Origins.Items
        foreach ($origin in $origins) {
            if ($origin.DomainName -like "*voice-assistant-ai-production-frontend*") {
                $distId = $dist.Id
                Write-Host "Found CloudFront distribution: $distId" -ForegroundColor Green
                Write-Host "Domain: $($dist.DomainName)" -ForegroundColor Cyan
                
                # Create invalidation
                Write-Host "Creating cache invalidation..." -ForegroundColor Yellow
                $invalidation = aws cloudfront create-invalidation --distribution-id $distId --paths "/*" --output json 2>$null
                
                if ($LASTEXITCODE -eq 0) {
                    Write-Host "Cache invalidation created successfully!" -ForegroundColor Green
                    Write-Host "Changes should be visible in 1-2 minutes." -ForegroundColor Cyan
                } else {
                    Write-Host "Failed to create invalidation" -ForegroundColor Red
                }
                exit 0
            }
        }
    }
    Write-Host "No matching CloudFront distribution found" -ForegroundColor Red
} else {
    Write-Host "No CloudFront distributions found" -ForegroundColor Red
}
