#!/usr/bin/env python3
"""
Force cache refresh by deploying with cache-busting headers
"""

import boto3
import os
import time
import mimetypes
from pathlib import Path

def deploy_with_cache_busting():
    """Deploy with aggressive cache-busting headers"""
    print("🔄 Deploying with cache-busting headers...")
    
    s3_client = boto3.client('s3', region_name='us-east-1')
    bucket_name = "nandhakumar-voice-assistant-prod"
    
    build_dir = Path("build")
    if not build_dir.exists():
        print("❌ Build directory not found")
        return False
    
    # Current timestamp for cache busting
    timestamp = str(int(time.time()))
    
    uploaded = 0
    
    for file_path in build_dir.rglob("*"):
        if file_path.is_file():
            s3_key = str(file_path.relative_to(build_dir)).replace("\\", "/")
            
            # Determine content type
            content_type, _ = mimetypes.guess_type(str(file_path))
            if content_type is None:
                content_type = 'binary/octet-stream'
            
            # Aggressive cache-busting for all files
            cache_control = 'no-cache, no-store, must-revalidate, max-age=0'
            
            # Additional headers to force refresh
            extra_args = {
                'ContentType': content_type,
                'CacheControl': cache_control,
                'Expires': 'Thu, 01 Jan 1970 00:00:00 GMT',
                'Metadata': {
                    'deployed-at': timestamp,
                    'cache-bust': 'true'
                }
            }
            
            try:
                s3_client.upload_file(
                    str(file_path),
                    bucket_name,
                    s3_key,
                    ExtraArgs=extra_args
                )
                uploaded += 1
                if uploaded % 5 == 0:
                    print(f"   Uploaded {uploaded} files with cache-busting...")
            except Exception as e:
                print(f"   ❌ Failed to upload {s3_key}: {e}")
    
    print(f"✅ Uploaded {uploaded} files with aggressive cache-busting")
    return True

def invalidate_cloudfront():
    """Invalidate CloudFront cache"""
    print("\n☁️ Invalidating CloudFront cache...")
    
    cloudfront = boto3.client('cloudfront', region_name='us-east-1')
    distribution_id = 'E2GA8IPSAF208X'
    
    try:
        response = cloudfront.create_invalidation(
            DistributionId=distribution_id,
            InvalidationBatch={
                'Paths': {
                    'Quantity': 1,
                    'Items': ['/*']
                },
                'CallerReference': f'cache-bust-{int(time.time())}'
            }
        )
        
        invalidation_id = response['Invalidation']['Id']
        print(f"✅ CloudFront invalidation created: {invalidation_id}")
        print("⏳ Invalidation will complete in 5-15 minutes")
        
        return True
        
    except Exception as e:
        print(f"❌ CloudFront invalidation failed: {e}")
        return False

def create_test_page():
    """Create a simple test page to verify cache busting"""
    print("\n📄 Creating cache-bust test page...")
    
    timestamp = int(time.time())
    test_html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Cache Bust Test</title>
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
    <meta http-equiv="Pragma" content="no-cache">
    <meta http-equiv="Expires" content="0">
</head>
<body>
    <h1>Cache Bust Test</h1>
    <p>Deployed at: {timestamp}</p>
    <p>If you see this timestamp, cache busting is working!</p>
    <script>
        console.log('Cache bust test loaded at:', {timestamp});
        alert('Cache busting successful! Timestamp: {timestamp}');
    </script>
</body>
</html>"""
    
    # Save test file
    with open('build/cache-test.html', 'w') as f:
        f.write(test_html)
    
    # Upload to S3
    s3_client = boto3.client('s3', region_name='us-east-1')
    bucket_name = "nandhakumar-voice-assistant-prod"
    
    try:
        s3_client.upload_file(
            'build/cache-test.html',
            bucket_name,
            'cache-test.html',
            ExtraArgs={
                'ContentType': 'text/html',
                'CacheControl': 'no-cache, no-store, must-revalidate, max-age=0',
                'Expires': 'Thu, 01 Jan 1970 00:00:00 GMT'
            }
        )
        
        test_url = f"http://{bucket_name}.s3-website-us-east-1.amazonaws.com/cache-test.html"
        print(f"✅ Test page created: {test_url}")
        
        # Clean up
        os.remove('build/cache-test.html')
        
        return test_url
        
    except Exception as e:
        print(f"❌ Failed to create test page: {e}")
        return None

def update_index_with_timestamp():
    """Update index.html with timestamp to force refresh"""
    print("\n📝 Adding timestamp to index.html...")
    
    index_path = Path("build/index.html")
    if not index_path.exists():
        print("❌ index.html not found")
        return False
    
    # Read current index.html
    with open(index_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add timestamp and cache-busting meta tags
    timestamp = int(time.time())
    cache_bust_meta = f'''
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
    <meta http-equiv="Pragma" content="no-cache">
    <meta http-equiv="Expires" content="0">
    <meta name="cache-bust" content="{timestamp}">
    <script>console.log('App loaded with cache-bust:', {timestamp});</script>
'''
    
    # Insert before closing head tag
    if '</head>' in content:
        content = content.replace('</head>', cache_bust_meta + '</head>')
    else:
        # Fallback: add at the beginning of body
        content = content.replace('<body>', f'<body>{cache_bust_meta}')
    
    # Write updated content
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Added cache-busting timestamp: {timestamp}")
    return True

def main():
    print("🚀 Force Cache Refresh Deployment")
    print("=" * 50)
    
    # Step 1: Update index.html with timestamp
    if update_index_with_timestamp():
        print("✅ Index.html updated with cache-busting")
    
    # Step 2: Deploy with cache-busting headers
    if deploy_with_cache_busting():
        print("✅ Files deployed with cache-busting")
    
    # Step 3: Create test page
    test_url = create_test_page()
    
    # Step 4: Invalidate CloudFront
    if invalidate_cloudfront():
        print("✅ CloudFront cache invalidated")
    
    print("\n" + "=" * 50)
    print("🎉 Cache-Busting Deployment Complete!")
    
    print("\n🌐 Test your app now:")
    print("   Main App: http://nandhakumar-voice-assistant-prod.s3-website-us-east-1.amazonaws.com")
    if test_url:
        print(f"   Test Page: {test_url}")
    
    print("\n💡 To force browser refresh:")
    print("   1. Press Ctrl+Shift+Delete (Clear cache)")
    print("   2. Or press Ctrl+F5 (Hard refresh)")
    print("   3. Or try incognito/private mode")
    print("   4. Or add ?v=" + str(int(time.time())) + " to the URL")
    
    print("\n✅ Cache-busting measures applied:")
    print("   • No-cache headers on all files")
    print("   • Timestamp added to index.html")
    print("   • CloudFront cache invalidated")
    print("   • Test page created for verification")
    
    print("\n🔄 The app should now load the latest version!")

if __name__ == "__main__":
    main()
