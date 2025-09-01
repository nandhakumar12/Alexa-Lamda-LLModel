#!/usr/bin/env python3
"""
Deploy with new API and complete cache busting
"""

import boto3
import os
import time
import json
from pathlib import Path

def deploy_with_new_api():
    """Deploy with new API and complete cache invalidation"""
    print("🚀 Deploying with New API & Complete Cache Busting")
    print("=" * 60)
    
    # S3 client
    s3 = boto3.client('s3')
    bucket_name = 'nandhakumar-voice-assistant-prod'
    
    # Build directory
    build_dir = Path('build')
    
    if not build_dir.exists():
        print("❌ Build directory not found. Run 'npm run build' first.")
        return
    
    # Add timestamp to index.html for cache busting
    timestamp = int(time.time())
    print(f"📝 Adding cache-busting timestamp: {timestamp}")
    
    index_path = build_dir / 'index.html'
    if index_path.exists():
        with open(index_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Add timestamp and new API info to HTML
        cache_bust_comment = f"""
<!-- Cache Bust: {timestamp} -->
<!-- New API: https://4po6882mz6.execute-api.us-east-1.amazonaws.com/prod -->
<!-- Deployed: {time.strftime('%Y-%m-%d %H:%M:%S')} -->
"""
        content = content.replace('<head>', f'<head>{cache_bust_comment}')
        
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Index.html updated with cache-busting")
    
    # Upload all files with no-cache headers
    print("🔄 Uploading files with aggressive no-cache headers...")
    
    uploaded_count = 0
    for root, dirs, files in os.walk(build_dir):
        for file in files:
            local_path = Path(root) / file
            relative_path = local_path.relative_to(build_dir)
            s3_key = str(relative_path).replace('\\', '/')
            
            # Determine content type
            content_type = 'text/html'
            if file.endswith('.js'):
                content_type = 'application/javascript'
            elif file.endswith('.css'):
                content_type = 'text/css'
            elif file.endswith('.json'):
                content_type = 'application/json'
            elif file.endswith('.png'):
                content_type = 'image/png'
            elif file.endswith('.jpg') or file.endswith('.jpeg'):
                content_type = 'image/jpeg'
            elif file.endswith('.svg'):
                content_type = 'image/svg+xml'
            elif file.endswith('.ico'):
                content_type = 'image/x-icon'
            
            # Ultra-aggressive no-cache headers
            cache_control = 'no-cache, no-store, must-revalidate, max-age=0'
            
            try:
                s3.upload_file(
                    str(local_path),
                    bucket_name,
                    s3_key,
                    ExtraArgs={
                        'ContentType': content_type,
                        'CacheControl': cache_control,
                        'Metadata': {
                            'timestamp': str(timestamp),
                            'new-api': 'true',
                            'cache-bust': 'aggressive'
                        }
                    }
                )
                uploaded_count += 1
                if uploaded_count % 5 == 0:
                    print(f"   Uploaded {uploaded_count} files with no-cache headers...")
                    
            except Exception as e:
                print(f"   ❌ Failed to upload {s3_key}: {e}")
    
    print(f"✅ Uploaded {uploaded_count} files with aggressive no-cache headers")
    
    # Create a special test page to verify new API
    test_page_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>API Test - New Gateway</title>
    <style>
        body {{ font-family: Arial, sans-serif; padding: 20px; background: #1a1a2e; color: white; }}
        .container {{ max-width: 800px; margin: 0 auto; }}
        .status {{ padding: 10px; margin: 10px 0; border-radius: 5px; }}
        .success {{ background: #4CAF50; }}
        .error {{ background: #f44336; }}
        .info {{ background: #2196F3; }}
        button {{ padding: 10px 20px; background: #9c27b0; color: white; border: none; border-radius: 5px; cursor: pointer; }}
        #response {{ background: #333; padding: 15px; border-radius: 5px; margin: 10px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔧 New API Gateway Test</h1>
        <div class="status info">
            <strong>New API URL:</strong> https://4po6882mz6.execute-api.us-east-1.amazonaws.com/prod/chatbot
        </div>
        <div class="status info">
            <strong>Timestamp:</strong> {timestamp}
        </div>
        <div class="status info">
            <strong>Deployed:</strong> {time.strftime('%Y-%m-%d %H:%M:%S')}
        </div>
        
        <button onclick="testNewAPI()">🧪 Test New API</button>
        <button onclick="clearCache()">🗑️ Clear Cache & Reload</button>
        
        <div id="response"></div>
        
        <script>
            async function testNewAPI() {{
                const responseDiv = document.getElementById('response');
                responseDiv.innerHTML = '⏳ Testing new API...';
                
                try {{
                    const response = await fetch('https://4po6882mz6.execute-api.us-east-1.amazonaws.com/prod/chatbot', {{
                        method: 'POST',
                        headers: {{
                            'Content-Type': 'application/json',
                        }},
                        body: JSON.stringify({{
                            message: 'Testing new API gateway',
                            type: 'text',
                            session_id: 'api-test-{timestamp}'
                        }})
                    }});
                    
                    if (response.ok) {{
                        const data = await response.json();
                        responseDiv.innerHTML = `
                            <div class="status success">
                                <strong>✅ New API Working!</strong><br>
                                Response: ${{data.response}}
                            </div>
                        `;
                    }} else {{
                        responseDiv.innerHTML = `
                            <div class="status error">
                                <strong>❌ API Error:</strong> ${{response.status}} - ${{response.statusText}}
                            </div>
                        `;
                    }}
                }} catch (error) {{
                    responseDiv.innerHTML = `
                        <div class="status error">
                            <strong>❌ Network Error:</strong> ${{error.message}}
                        </div>
                    `;
                }}
            }}
            
            function clearCache() {{
                if ('caches' in window) {{
                    caches.keys().then(names => {{
                        names.forEach(name => {{
                            caches.delete(name);
                        }});
                    }});
                }}
                location.reload(true);
            }}
            
            // Auto-test on load
            window.onload = () => {{
                setTimeout(testNewAPI, 1000);
            }};
        </script>
    </div>
</body>
</html>"""
    
    # Upload test page
    try:
        s3.put_object(
            Bucket=bucket_name,
            Key='new-api-test.html',
            Body=test_page_content,
            ContentType='text/html',
            CacheControl='no-cache, no-store, must-revalidate'
        )
        print("✅ New API test page created")
    except Exception as e:
        print(f"❌ Failed to create test page: {e}")
    
    # Invalidate CloudFront cache
    print("☁️ Invalidating CloudFront cache...")
    try:
        cloudfront = boto3.client('cloudfront')
        
        # Get distribution ID (you might need to update this)
        distributions = cloudfront.list_distributions()
        distribution_id = None
        
        for dist in distributions['DistributionList']['Items']:
            if 'nandhakumar-voice-assistant' in dist['Comment']:
                distribution_id = dist['Id']
                break
        
        if distribution_id:
            invalidation = cloudfront.create_invalidation(
                DistributionId=distribution_id,
                InvalidationBatch={{
                    'Paths': {{
                        'Quantity': 1,
                        'Items': ['/*']
                    }},
                    'CallerReference': f'cache-bust-{timestamp}'
                }}
            )
            print(f"✅ CloudFront invalidation created: {invalidation['Invalidation']['Id']}")
        else:
            print("⚠️  CloudFront distribution not found")
            
    except Exception as e:
        print(f"⚠️  CloudFront invalidation failed: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Deployment Complete with New API!")
    
    base_url = "http://nandhakumar-voice-assistant-prod.s3-website-us-east-1.amazonaws.com"
    
    print(f"\n🌐 Test URLs:")
    print(f"   Main App: {base_url}")
    print(f"   Cache-Busted: {base_url}?v={timestamp}&new-api=true")
    print(f"   New API Test: {base_url}/new-api-test.html")
    
    print(f"\n✅ New API Gateway: https://4po6882mz6.execute-api.us-east-1.amazonaws.com/prod")
    print(f"✅ Cache-Busting Timestamp: {timestamp}")
    print(f"✅ All files uploaded with no-cache headers")
    
    print(f"\n💡 To force fresh load:")
    print(f"   1. Open: {base_url}/new-api-test.html")
    print(f"   2. Or use: {base_url}?v={timestamp}&fresh=true")
    print(f"   3. Or clear browser cache completely")

if __name__ == "__main__":
    deploy_with_new_api()
