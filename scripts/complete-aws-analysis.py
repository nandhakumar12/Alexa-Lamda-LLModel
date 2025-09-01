#!/usr/bin/env python3
"""
Complete AWS Infrastructure Analysis & Fix
Analyze Lambda, API Gateway, VPC, IAM, and all related services
"""

import boto3
import json
import time
from botocore.exceptions import ClientError

def analyze_aws_infrastructure():
    """Complete analysis of all AWS services"""
    print("🔍 COMPLETE AWS INFRASTRUCTURE ANALYSIS")
    print("=" * 80)
    
    # Initialize clients
    lambda_client = boto3.client('lambda')
    apigateway_client = boto3.client('apigateway')
    iam_client = boto3.client('iam')
    ec2_client = boto3.client('ec2')
    logs_client = boto3.client('logs')
    
    analysis_results = {}
    
    # 1. LAMBDA FUNCTION ANALYSIS
    print("\n1️⃣ LAMBDA FUNCTION ANALYSIS")
    print("-" * 40)
    
    try:
        # Get Lambda function details
        function_name = 'voice-assistant-chatbot'
        lambda_config = lambda_client.get_function(FunctionName=function_name)
        
        print(f"✅ Lambda Function: {function_name}")
        print(f"   Runtime: {lambda_config['Configuration']['Runtime']}")
        print(f"   Handler: {lambda_config['Configuration']['Handler']}")
        print(f"   Timeout: {lambda_config['Configuration']['Timeout']}s")
        print(f"   Memory: {lambda_config['Configuration']['MemorySize']}MB")
        
        # Check VPC configuration
        vpc_config = lambda_config['Configuration'].get('VpcConfig', {})
        if vpc_config.get('VpcId'):
            print(f"   🌐 VPC ID: {vpc_config['VpcId']}")
            print(f"   🔒 Security Groups: {vpc_config.get('SecurityGroupIds', [])}")
            print(f"   🏠 Subnets: {vpc_config.get('SubnetIds', [])}")
            analysis_results['lambda_in_vpc'] = True
        else:
            print("   🌍 No VPC (runs in AWS managed VPC)")
            analysis_results['lambda_in_vpc'] = False
        
        # Check execution role
        role_arn = lambda_config['Configuration']['Role']
        print(f"   👤 Execution Role: {role_arn}")
        
        # Get role details
        role_name = role_arn.split('/')[-1]
        try:
            role_details = iam_client.get_role(RoleName=role_name)
            print(f"   📋 Role Created: {role_details['Role']['CreateDate']}")
            
            # Get attached policies
            attached_policies = iam_client.list_attached_role_policies(RoleName=role_name)
            print(f"   📜 Attached Policies:")
            for policy in attached_policies['AttachedPolicies']:
                print(f"      - {policy['PolicyName']}")
                
        except Exception as e:
            print(f"   ❌ Role analysis failed: {e}")
        
        analysis_results['lambda_config'] = lambda_config['Configuration']
        
    except Exception as e:
        print(f"❌ Lambda analysis failed: {e}")
        analysis_results['lambda_error'] = str(e)
    
    # 2. API GATEWAY ANALYSIS
    print("\n2️⃣ API GATEWAY ANALYSIS")
    print("-" * 40)
    
    try:
        # Get all APIs
        apis = apigateway_client.get_rest_apis()
        
        target_api = None
        for api in apis['items']:
            if 'voice-assistant' in api['name'].lower():
                target_api = api
                break
        
        if target_api:
            api_id = target_api['id']
            print(f"✅ API Gateway: {target_api['name']} ({api_id})")
            print(f"   Created: {target_api['createdDate']}")
            print(f"   Endpoint: https://{api_id}.execute-api.us-east-1.amazonaws.com")
            
            # Get resources
            resources = apigateway_client.get_resources(restApiId=api_id)
            print(f"   📁 Resources:")
            for resource in resources['items']:
                print(f"      - {resource['path']} ({resource['id']})")
                
                # Check methods for each resource
                if 'resourceMethods' in resource:
                    for method in resource['resourceMethods']:
                        print(f"        └─ {method}")
                        
                        # Get method details
                        try:
                            method_details = apigateway_client.get_method(
                                restApiId=api_id,
                                resourceId=resource['id'],
                                httpMethod=method
                            )
                            
                            # Check CORS
                            if 'methodResponses' in method_details:
                                for status_code, response in method_details['methodResponses'].items():
                                    headers = response.get('responseParameters', {})
                                    cors_headers = [h for h in headers.keys() if 'Access-Control' in h]
                                    if cors_headers:
                                        print(f"           ✅ CORS headers: {len(cors_headers)}")
                                    else:
                                        print(f"           ❌ No CORS headers for {status_code}")
                            
                        except Exception as e:
                            print(f"           ❌ Method details failed: {e}")
            
            # Check deployments
            deployments = apigateway_client.get_deployments(restApiId=api_id)
            print(f"   🚀 Deployments: {len(deployments['items'])}")
            if deployments['items']:
                latest = deployments['items'][0]
                print(f"      Latest: {latest['id']} ({latest['createdDate']})")
            
            analysis_results['api_gateway'] = target_api
            
        else:
            print("❌ No voice-assistant API found")
            analysis_results['api_gateway_error'] = "API not found"
            
    except Exception as e:
        print(f"❌ API Gateway analysis failed: {e}")
        analysis_results['api_gateway_error'] = str(e)
    
    # 3. VPC & NETWORK ANALYSIS
    print("\n3️⃣ VPC & NETWORK ANALYSIS")
    print("-" * 40)
    
    if analysis_results.get('lambda_in_vpc'):
        try:
            vpc_id = lambda_config['Configuration']['VpcConfig']['VpcId']
            
            # Get VPC details
            vpcs = ec2_client.describe_vpcs(VpcIds=[vpc_id])
            vpc = vpcs['Vpcs'][0]
            print(f"✅ VPC: {vpc_id}")
            print(f"   CIDR: {vpc['CidrBlock']}")
            print(f"   State: {vpc['State']}")
            
            # Get security groups
            sg_ids = lambda_config['Configuration']['VpcConfig']['SecurityGroupIds']
            if sg_ids:
                sgs = ec2_client.describe_security_groups(GroupIds=sg_ids)
                print(f"   🔒 Security Groups:")
                for sg in sgs['SecurityGroups']:
                    print(f"      - {sg['GroupName']} ({sg['GroupId']})")
                    
                    # Check outbound rules
                    print(f"        Outbound Rules:")
                    for rule in sg['IpPermissions']:
                        print(f"          - {rule}")
            
            # Get subnets
            subnet_ids = lambda_config['Configuration']['VpcConfig']['SubnetIds']
            if subnet_ids:
                subnets = ec2_client.describe_subnets(SubnetIds=subnet_ids)
                print(f"   🏠 Subnets:")
                for subnet in subnets['Subnets']:
                    print(f"      - {subnet['SubnetId']} ({subnet['AvailabilityZone']})")
                    print(f"        CIDR: {subnet['CidrBlock']}")
                    print(f"        Public: {subnet.get('MapPublicIpOnLaunch', False)}")
            
        except Exception as e:
            print(f"❌ VPC analysis failed: {e}")
    else:
        print("✅ Lambda not in VPC - using AWS managed networking")
    
    # 4. CLOUDWATCH LOGS ANALYSIS
    print("\n4️⃣ CLOUDWATCH LOGS ANALYSIS")
    print("-" * 40)
    
    try:
        log_group_name = f'/aws/lambda/{function_name}'
        
        # Get recent log streams
        log_streams = logs_client.describe_log_streams(
            logGroupName=log_group_name,
            orderBy='LastEventTime',
            descending=True,
            limit=5
        )
        
        print(f"✅ Log Group: {log_group_name}")
        print(f"   Recent Streams: {len(log_streams['logStreams'])}")
        
        if log_streams['logStreams']:
            latest_stream = log_streams['logStreams'][0]
            print(f"   Latest: {latest_stream['logStreamName']}")
            print(f"   Last Event: {latest_stream.get('lastEventTime', 'N/A')}")
            
            # Get recent log events
            try:
                events = logs_client.get_log_events(
                    logGroupName=log_group_name,
                    logStreamName=latest_stream['logStreamName'],
                    limit=10,
                    startFromHead=False
                )
                
                print(f"   📝 Recent Events:")
                for event in events['events'][-5:]:  # Last 5 events
                    timestamp = time.strftime('%Y-%m-%d %H:%M:%S', 
                                            time.localtime(event['timestamp']/1000))
                    message = event['message'].strip()
                    if len(message) > 100:
                        message = message[:100] + "..."
                    print(f"      {timestamp}: {message}")
                    
            except Exception as e:
                print(f"   ❌ Log events failed: {e}")
        
    except Exception as e:
        print(f"❌ CloudWatch logs analysis failed: {e}")
    
    # 5. ENVIRONMENT VARIABLES & CONFIGURATION
    print("\n5️⃣ ENVIRONMENT & CONFIGURATION")
    print("-" * 40)
    
    try:
        env_vars = lambda_config['Configuration'].get('Environment', {}).get('Variables', {})
        print(f"✅ Environment Variables: {len(env_vars)}")
        for key, value in env_vars.items():
            if 'key' in key.lower() or 'secret' in key.lower():
                print(f"   {key}: ***HIDDEN***")
            else:
                print(f"   {key}: {value}")
                
    except Exception as e:
        print(f"❌ Environment analysis failed: {e}")
    
    return analysis_results

if __name__ == "__main__":
    results = analyze_aws_infrastructure()
    
    print("\n" + "=" * 80)
    print("📊 ANALYSIS SUMMARY")
    print("=" * 80)
    
    # Print key findings
    if 'lambda_config' in results:
        print("✅ Lambda function found and analyzed")
    else:
        print("❌ Lambda function issues detected")
    
    if 'api_gateway' in results:
        print("✅ API Gateway found and analyzed")
    else:
        print("❌ API Gateway issues detected")
    
    if results.get('lambda_in_vpc'):
        print("⚠️  Lambda is in VPC - check network configuration")
    else:
        print("✅ Lambda uses AWS managed networking")
    
    print(f"\n💾 Analysis results saved to analysis_results.json")
    
    # Save results
    with open('analysis_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
