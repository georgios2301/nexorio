#!/usr/bin/env python3
import requests

# Test with a real delivery note image if available
# First, let's check what test images might be available
import os
import glob

# Look for test images
test_files = []
for pattern in ['*.jpg', '*.jpeg', '*.png', '*.pdf']:
    test_files.extend(glob.glob(f'Lieferschein/Vorlagen/{pattern}'))
    test_files.extend(glob.glob(f'Lieferschein/Programm/{pattern}'))

if test_files:
    print(f"Found test files: {test_files}")
    # Use the first one
    test_file = test_files[0]
    print(f"Testing with: {test_file}")
    
    with open(test_file, 'rb') as f:
        files = {'file': (os.path.basename(test_file), f, 'application/octet-stream')}
        response = requests.post('http://localhost:8001/api/extract', files=files)
    
    print(f'Status Code: {response.status_code}')
    print(f'Response: {response.text[:500]}...' if len(response.text) > 500 else response.text)
else:
    print("No test images found. Testing with minimal PNG...")
    # Create minimal PNG
    import base64
    png_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
    png_data = base64.b64decode(png_base64)
    
    with open('test_minimal.png', 'wb') as f:
        f.write(png_data)
    
    with open('test_minimal.png', 'rb') as f:
        files = {'file': ('test_minimal.png', f, 'image/png')}
        response = requests.post('http://localhost:8001/api/extract', files=files)
    
    print(f'Status Code: {response.status_code}')
    print(f'Response: {response.text}')
    
    os.remove('test_minimal.png')