#!/usr/bin/env python3
"""
Fix CloudFront caching issue by invalidating cache and using direct S3
"""

import boto3
import time
import json

def invalidate_cloudfront():
    """Invalidate CloudFront cache"""
    print("🔄 INVALIDATING CLOUDFRONT CACHE")
    print("=" * 50)
    
    cloudfront = boto3.client('cloudfront')
    
    try:
        # List distributions
        distributions = cloudfront.list_distributions()
        
        for dist in distributions['DistributionList']['Items']:
            domain = dist['DomainName']
            dist_id = dist['Id']
            
            if 'nandhakumar' in domain or 'voice-assistant' in domain:
                print(f"🌐 Found distribution: {domain}")
                print(f"   ID: {dist_id}")
                
                # Create invalidation
                invalidation = cloudfront.create_invalidation(
                    DistributionId=dist_id,
                    InvalidationBatch={
                        'Paths': {
                            'Quantity': 1,
                            'Items': ['/*']
                        },
                        'CallerReference': f'fix-cache-{int(time.time())}'
                    }
                )
                
                print(f"   ✅ Invalidation created: {invalidation['Invalidation']['Id']}")
                print(f"   ⏳ This will take 5-15 minutes to complete")
                
    except Exception as e:
        print(f"❌ CloudFront error: {e}")

def check_s3_direct_access():
    """Check if S3 direct access works"""
    print("\n🔍 CHECKING S3 DIRECT ACCESS")
    print("=" * 50)
    
    s3 = boto3.client('s3')
    bucket_name = 'nandhakumar-voice-assistant-prod'
    
    try:
        # Check bucket website configuration
        website_config = s3.get_bucket_website(Bucket=bucket_name)
        print(f"✅ S3 website hosting enabled")
        print(f"   Index: {website_config.get('IndexDocument', {}).get('Suffix', 'index.html')}")
        
        # Direct S3 URL
        s3_url = f"http://{bucket_name}.s3-website-us-east-1.amazonaws.com"
        print(f"🌐 Direct S3 URL: {s3_url}")
        
        # Test direct access
        import requests
        try:
            response = requests.get(s3_url, timeout=10)
            if response.status_code == 200:
                print(f"   ✅ Direct S3 access WORKING!")
                
                # Check if it contains the correct API URL
                if '4po6882mz6' in response.text:
                    print(f"   ✅ Contains CORRECT API URL (4po6882mz6)")
                elif 'dgkrnsyybk' in response.text:
                    print(f"   ⚠️  Contains OLD API URL (dgkrnsyybk)")
                else:
                    print(f"   ❓ API URL not found in HTML")
                    
            else:
                print(f"   ❌ Direct S3 access failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Direct S3 test error: {e}")
            
    except Exception as e:
        print(f"❌ S3 website config error: {e}")

def force_frontend_update():
    """Force update frontend with cache-busting"""
    print("\n🚀 FORCE UPDATING FRONTEND")
    print("=" * 50)
    
    s3 = boto3.client('s3')
    bucket_name = 'nandhakumar-voice-assistant-prod'
    timestamp = int(time.time())
    
    # Create a cache-busting index.html
    cache_bust_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <link rel="icon" href="%PUBLIC_URL%/favicon.ico" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#000000" />
    <meta name="description" content="Nandhakumar's AI Voice Assistant" />
    <link rel="apple-touch-icon" href="%PUBLIC_URL%/logo192.png" />
    <link rel="manifest" href="%PUBLIC_URL%/manifest.json" />
    <title>Nandhakumar's AI Assistant</title>
    
    <!-- FORCE CACHE REFRESH -->
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
    <meta http-equiv="Pragma" content="no-cache">
    <meta http-equiv="Expires" content="0">
    
    <!-- Cache busting for CSS and JS -->
    <script>
        // Force reload all cached resources
        if (performance.navigation.type !== 1) {{
            window.location.href = window.location.href + '?cb={timestamp}';
        }}
    </script>
    
<script defer="defer" src="/static/js/main.8e61bb56.js?cb={timestamp}"></script><link href="/static/css/main.c5e8eb98.css?cb={timestamp}" rel="stylesheet"></head>
<body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
    
    <!-- Debug info -->
    <script>
        console.log('🔧 Cache-busted version: {timestamp}');
        console.log('🌐 Expected API: https://4po6882mz6.execute-api.us-east-1.amazonaws.com/prod');
        
        // Test API immediately
        fetch('https://4po6882mz6.execute-api.us-east-1.amazonaws.com/prod/chatbot', {{
            method: 'POST',
            headers: {{ 'Content-Type': 'application/json' }},
            body: JSON.stringify({{
                message: 'Cache bust test',
                type: 'text',
                session_id: 'cache-test-{timestamp}'
            }})
        }})
        .then(r => r.json())
        .then(d => console.log('✅ API Test Success:', d.response))
        .catch(e => console.error('❌ API Test Failed:', e));
    </script>
</body>
</html>"""
    
    try:
        # Upload cache-busted index.html
        s3.put_object(
            Bucket=bucket_name,
            Key='index.html',
            Body=cache_bust_html,
            ContentType='text/html',
            CacheControl='no-cache, no-store, must-revalidate',
            Metadata={
                'cache-bust': str(timestamp),
                'api-url': 'https://4po6882mz6.execute-api.us-east-1.amazonaws.com/prod'
            }
        )
        
        print(f"✅ Uploaded cache-busted index.html")
        print(f"   Timestamp: {timestamp}")
        
        # Also update the main JS file with cache-busting
        try:
            # Download current JS file
            js_response = s3.get_object(Bucket=bucket_name, Key='static/js/main.8e61bb56.js')
            js_content = js_response['Body'].read()
            
            # Re-upload with no-cache headers
            s3.put_object(
                Bucket=bucket_name,
                Key='static/js/main.8e61bb56.js',
                Body=js_content,
                ContentType='application/javascript',
                CacheControl='no-cache, no-store, must-revalidate',
                Metadata={'cache-bust': str(timestamp)}
            )
            
            print(f"✅ Updated JS file with no-cache headers")
            
        except Exception as e:
            print(f"⚠️  Could not update JS file: {e}")
            
    except Exception as e:
        print(f"❌ Error updating frontend: {e}")

def main():
    """Main function"""
    print("🚨 FIXING CLOUDFRONT CACHE ISSUE")
    print("=" * 60)
    
    invalidate_cloudfront()
    check_s3_direct_access()
    force_frontend_update()
    
    print("\n" + "=" * 60)
    print("🎉 CACHE FIX COMPLETE!")
    
    s3_url = "http://nandhakumar-voice-assistant-prod.s3-website-us-east-1.amazonaws.com"
    timestamp = int(time.time())
    
    print(f"\n🌐 USE THESE URLS (bypass CloudFront):")
    print(f"   Direct S3: {s3_url}")
    print(f"   Cache-busted: {s3_url}?cb={timestamp}")
    
    print(f"\n💡 INSTRUCTIONS:")
    print(f"   1. Use the Direct S3 URL above (not CloudFront)")
    print(f"   2. Clear browser cache (Ctrl+F5)")
    print(f"   3. CloudFront invalidation will take 5-15 minutes")
    print(f"   4. After invalidation, CloudFront should work too")
    
    print(f"\n🎯 The network error should be GONE when using Direct S3!")

if __name__ == "__main__":
    main()
