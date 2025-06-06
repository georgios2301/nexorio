import requests

# Create a minimal test file
with open('test.txt', 'w') as f:
    f.write('Test content')

# Send request
with open('test.txt', 'rb') as f:
    files = {'file': ('test.txt', f, 'text/plain')}
    response = requests.post('http://localhost:8001/api/extract', files=files)

print(f'Status Code: {response.status_code}')
print(f'Response Headers: {dict(response.headers)}')
print(f'Response: {response.text}')

# Clean up
import os
os.remove('test.txt')