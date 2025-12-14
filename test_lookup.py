import requests

# Test profile lookup
response = requests.post('http://localhost:5000/api/lookup-profile', 
                        json={'username': 'instagram'})

print(f'Status: {response.status_code}')
data = response.json()
print(f'Success: {data.get("success")}')

if data.get('success'):
    profile = data['profile']
    print(f'\n✓ Profile Found:')
    print(f'  Username: @{profile["username"]}')
    print(f'  Full Name: {profile["full_name"]}')
    print(f'  Followers: {profile["follower_count"]:,}')
    print(f'  Private: {profile["is_private"]}')
else:
    print(f'\n✗ Error: {data.get("error")}')
