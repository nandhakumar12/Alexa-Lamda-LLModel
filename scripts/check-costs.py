#!/usr/bin/env python3

"""
Check current AWS costs for Voice Assistant LLM
"""

import boto3
from datetime import datetime, timedelta

def check_costs():
    print("💰 Voice Assistant AI - Cost Check")
    print("=" * 50)
    
    try:
        ce = boto3.client('ce', region_name='us-east-1')
        
        # Get last 30 days
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)
        
        response = ce.get_cost_and_usage(
            TimePeriod={
                'Start': start_date.strftime('%Y-%m-%d'),
                'End': end_date.strftime('%Y-%m-%d')
            },
            Granularity='MONTHLY',
            Metrics=['BlendedCost'],
            GroupBy=[
                {
                    'Type': 'DIMENSION',
                    'Key': 'SERVICE'
                }
            ]
        )
        
        print(f"📅 Period: {start_date} to {end_date}")
        print("\n💸 Service Costs:")
        print("-" * 30)
        
        total_cost = 0
        for result in response['ResultsByTime']:
            for group in result['Groups']:
                service = group['Keys'][0]
                cost = float(group['Metrics']['BlendedCost']['Amount'])
                if cost > 0:
                    print(f"{service}: ${cost:.2f}")
                    total_cost += cost
        
        print("-" * 30)
        print(f"💰 Total: ${total_cost:.2f}")
        
        if total_cost < 5:
            print("✅ Excellent! Very low costs")
        elif total_cost < 15:
            print("✅ Good! Reasonable costs")
        else:
            print("⚠️ Consider optimization")
            
    except Exception as e:
        print(f"❌ Error checking costs: {e}")
        print("💡 Make sure you have Cost Explorer permissions")

if __name__ == "__main__":
    check_costs()
