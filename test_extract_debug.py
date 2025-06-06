#!/usr/bin/env python3
import requests
import base64

# Create a simple PNG image using base64 (1x1 white pixel)
png_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
png_data = base64.b64decode(png_base64)

# Save to file
with open('test_image.png', 'wb') as f:
    f.write(png_data)

# Send request
with open('test_image.png', 'rb') as f:
    files = {'file': ('test_image.png', f, 'image/png')}
    response = requests.post('http://localhost:8001/api/extract', files=files)

print(f'Status Code: {response.status_code}')
print(f'Response: {response.text}')

# Clean up
import os
os.remove('test_image.png')