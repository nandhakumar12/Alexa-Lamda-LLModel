#!/usr/bin/env python3
"""
Check what's actually deployed in the frontend
"""

import boto3
import requests

def check_s3_deployment():
    """Check what's actually in S3"""
    print("🔍 CHECKING S3 DEPLOYMENT")
    print("=" * 50)
    
    s3 = boto3.client('s3')
    bucket_name = 'nandhakumar-voice-assistant-prod'
    
    try:
        # List all objects
        objects = s3.list_objects_v2(Bucket=bucket_name)
        
        if 'Contents' in objects:
            print(f"📁 Found {len(objects['Contents'])} files in S3:")
            
            for obj in objects['Contents']:
                key = obj['Key']
                size = obj['Size']
                modified = obj['LastModified']
                print(f"   {key} ({size} bytes, {modified})")
                
                # Check specific files
                if key == 'index.html':
                    print(f"   📄 Downloading index.html to check content...")
                    
                    try:
                        response = s3.get_object(Bucket=bucket_name, Key='index.html')
                        content = response['Body'].read().decode('utf-8')
                        
                        print(f"   📝 Index.html content preview:")
                        lines = content.split('\n')[:10]
                        for line in lines:
                            if line.strip():
                                print(f"      {line.strip()}")
                        
                        # Check for API URL
                        if '4po6882mz6' in content:
                            print(f"   ✅ Contains CORRECT API URL (4po6882mz6)")
                        elif 'dgkrnsyybk' in content:
                            print(f"   ❌ Contains OLD API URL (dgkrnsyybk)")
                        else:
                            print(f"   ❓ No API URL found in index.html")
                            
                        # Check for JavaScript files
                        if 'main.' in content and '.js' in content:
                            print(f"   📜 JavaScript files referenced in index.html")
                        
                    except Exception as e:
                        print(f"   ❌ Error reading index.html: {e}")
                        
        else:
            print("❌ No files found in S3 bucket")
            
    except Exception as e:
        print(f"❌ Error checking S3: {e}")

def check_js_files():
    """Check the JavaScript files for API URL"""
    print("\n🔍 CHECKING JAVASCRIPT FILES")
    print("=" * 50)
    
    s3 = boto3.client('s3')
    bucket_name = 'nandhakumar-voice-assistant-prod'
    
    try:
        # List objects in static/js/
        objects = s3.list_objects_v2(Bucket=bucket_name, Prefix='static/js/')
        
        if 'Contents' in objects:
            for obj in objects['Contents']:
                key = obj['Key']
                if key.endswith('.js') and 'main.' in key:
                    print(f"📜 Checking {key}...")
                    
                    try:
                        response = s3.get_object(Bucket=bucket_name, Key=key)
                        content = response['Body'].read().decode('utf-8')
                        
                        # Check for API URLs
                        if '4po6882mz6' in content:
                            print(f"   ✅ Contains CORRECT API URL (4po6882mz6)")
                        elif 'dgkrnsyybk' in content:
                            print(f"   ❌ Contains OLD API URL (dgkrnsyybk)")
                        else:
                            print(f"   ❓ No API URL found in JS file")
                            
                        # Check for auth bypass
                        if 'REACT_APP_SKIP_AUTH' in content:
                            print(f"   ✅ Contains auth bypass logic")
                        else:
                            print(f"   ❓ No auth bypass found")
                            
                    except Exception as e:
                        print(f"   ❌ Error reading {key}: {e}")
                        
    except Exception as e:
        print(f"❌ Error checking JS files: {e}")

def test_direct_url():
    """Test the direct URL"""
    print("\n🌐 TESTING DIRECT URL")
    print("=" * 50)
    
    url = "http://nandhakumar-voice-assistant-prod.s3-website-us-east-1.amazonaws.com"
    
    try:
        response = requests.get(url, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            content = response.text
            print(f"Content length: {len(content)} characters")
            
            # Show first few lines
            lines = content.split('\n')[:15]
            print(f"First 15 lines:")
            for i, line in enumerate(lines, 1):
                if line.strip():
                    print(f"   {i:2d}: {line.strip()}")
                    
        else:
            print(f"❌ Failed to load: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing URL: {e}")

def force_redeploy():
    """Force redeploy with correct files"""
    print("\n🚀 FORCE REDEPLOYING CORRECT FILES")
    print("=" * 50)
    
    s3 = boto3.client('s3')
    bucket_name = 'nandhakumar-voice-assistant-prod'
    
    # Create a proper index.html with correct API URL
    correct_index = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <link rel="icon" href="/favicon.ico" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#000000" />
    <meta name="description" content="Nandhakumar's AI Voice Assistant" />
    <title>Nandhakumar's AI Assistant</title>
    
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
    <meta http-equiv="Pragma" content="no-cache">
    <meta http-equiv="Expires" content="0">
    
<script defer="defer" src="/static/js/main.71bd39b5.js"></script><link href="/static/css/main.c5e8eb98.css" rel="stylesheet"></head>
<body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
    
    <script>
        console.log('🔧 Correct version loaded');
        console.log('🌐 API URL should be: https://4po6882mz6.execute-api.us-east-1.amazonaws.com/prod');
        console.log('🔓 Auth bypass should be enabled');
        
        // Test API on load
        window.addEventListener('load', function() {
            setTimeout(() => {
                fetch('https://4po6882mz6.execute-api.us-east-1.amazonaws.com/prod/chatbot', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        message: 'Frontend load test',
                        type: 'text',
                        session_id: 'frontend-load-test'
                    })
                })
                .then(r => r.json())
                .then(d => console.log('✅ API Test from Frontend:', d.response))
                .catch(e => console.error('❌ API Test Failed:', e));
            }, 2000);
        });
    </script>
</body>
</html>"""
    
    try:
        # Upload correct index.html
        s3.put_object(
            Bucket=bucket_name,
            Key='index.html',
            Body=correct_index,
            ContentType='text/html',
            CacheControl='no-cache, no-store, must-revalidate'
        )
        
        print("✅ Uploaded corrected index.html")
        
    except Exception as e:
        print(f"❌ Error uploading: {e}")

def main():
    """Main function"""
    print("🚨 CHECKING FRONTEND DEPLOYMENT")
    print("=" * 60)
    
    check_s3_deployment()
    check_js_files()
    test_direct_url()
    force_redeploy()
    
    print("\n" + "=" * 60)
    print("🎯 DEPLOYMENT CHECK COMPLETE")
    
    print(f"\n🌐 TRY THIS URL:")
    print(f"   http://nandhakumar-voice-assistant-prod.s3-website-us-east-1.amazonaws.com")
    
    print(f"\n💡 CLEAR YOUR BROWSER CACHE AND TRY AGAIN!")

if __name__ == "__main__":
    main()
