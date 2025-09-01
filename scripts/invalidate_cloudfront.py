import boto3
import json

cloudfront = boto3.client('cloudfront')

try:
    # List all distributions
    response = cloudfront.list_distributions()
    
    if 'DistributionList' in response and 'Items' in response['DistributionList']:
        distributions = response['DistributionList']['Items']
        
        print("CloudFront Distributions:")
        for dist in distributions:
            print(f"  ID: {dist['Id']}")
            print(f"  Domain: {dist['DomainName']}")
            print(f"  Comment: {dist.get('Comment', 'No comment')}")
            print(f"  Status: {dist['Status']}")
            
            # Check if this is likely our voice assistant distribution
            if ('voice' in dist.get('Comment', '').lower() or 
                'assistant' in dist.get('Comment', '').lower() or
                'd3hl87po6y2b5n' in dist['DomainName']):
                
                print(f"  ✅ Found Voice Assistant distribution!")
                
                # Create invalidation
                invalidation_response = cloudfront.create_invalidation(
                    DistributionId=dist['Id'],
                    InvalidationBatch={
                        'Paths': {
                            'Quantity': 1,
                            'Items': ['/*']
                        },
                        'CallerReference': f"invalidation-{dist['Id']}-{int(__import__('time').time())}"
                    }
                )
                
                print(f"  ✅ Invalidation created: {invalidation_response['Invalidation']['Id']}")
                print(f"  🌐 Updated frontend will be available at: https://{dist['DomainName']}")
                break
            print()
    else:
        print("No CloudFront distributions found")
        
except Exception as e:
    print(f"Error: {e}")
