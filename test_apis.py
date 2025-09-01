import requests

# Test the API that's working with Claude
working_api = 'https://aj6fadvnlj.execute-api.us-east-1.amazonaws.com/prod/chatbot'

# Test the APIs mentioned in frontend code
old_apis = [
    'https://tcuzlzq1af.execute-api.us-east-1.amazonaws.com/prod/chatbot',
    'https://4po6882mz6.execute-api.us-east-1.amazonaws.com/prod/chatbot'
]

print('Testing APIs:')
print('=' * 50)

# Test working API
try:
    response = requests.post(working_api, json={'message': 'Hello', 'session_id': 'test'}, timeout=10)
    print(f'✅ WORKING API (aj6fadvnlj): {response.status_code}')
    if response.status_code == 200:
        data = response.json()
        print(f'   Model: {data.get("model", "unknown")}')
        print(f'   Response: {data.get("response", "")[:50]}...')
except Exception as e:
    print(f'❌ WORKING API (aj6fadvnlj): Error - {e}')

print()

# Test old APIs
for api in old_apis:
    try:
        response = requests.post(api, json={'message': 'Hello', 'session_id': 'test'}, timeout=10)
        api_id = api.split('//')[1].split('.')[0]
        print(f'📊 OLD API ({api_id}): {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            print(f'   Model: {data.get("model", "unknown")}')
            print(f'   Response: {data.get("response", "")[:50]}...')
    except Exception as e:
        api_id = api.split('//')[1].split('.')[0]
        print(f'❌ OLD API ({api_id}): Error - {e}')
    print()
