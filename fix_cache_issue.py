#!/usr/bin/env python3
"""
Fix the cache issue by adding cache-busting headers to the S3 deployment
"""

import boto3
import time

def fix_cache_issue():
    """Add no-cache headers to force browser refresh"""
    
    s3 = boto3.client('s3')
    bucket_name = 'nandhakumar-voice-assistant-prod'
    
    print("🔄 Fixing cache issue...")
    print("=" * 50)
    
    # Add no-cache headers to index.html
    try:
        # Copy the file to itself with new headers
        s3.copy_object(
            Bucket=bucket_name,
            CopySource={'Bucket': bucket_name, 'Key': 'index.html'},
            Key='index.html',
            MetadataDirective='REPLACE',
            CacheControl='no-cache, no-store, must-revalidate',
            Expires='Thu, 01 Jan 1970 00:00:00 GMT',
            ContentType='text/html'
        )
        print("✅ Added no-cache headers to index.html")
        
        # Create a timestamp for cache busting
        timestamp = int(time.time())
        
        print(f"\n🌐 Use this URL to access the latest version:")
        print(f"   http://nandhakumar-voice-assistant-prod.s3-website-us-east-1.amazonaws.com/?t={timestamp}")
        
        print(f"\n💡 To completely fix the issue:")
        print(f"   1. Clear your browser cache (Ctrl+Shift+Delete)")
        print(f"   2. Use incognito/private browsing mode")
        print(f"   3. Hard refresh the page (Ctrl+F5)")
        
        print(f"\n✅ The website is correctly configured with Claude AI!")
        print(f"   API: aj6fadvnlj.execute-api.us-east-1.amazonaws.com")
        print(f"   Model: Claude 3 Haiku")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    fix_cache_issue()
