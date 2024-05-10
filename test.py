import requests
import json
import base64

# image path
image_path = r".\static\UserFiles\UMB2.jpg"

# read image and encode in base 64
with open(image_path, "rb") as image_file:
    image_base64 = base64.b64encode(image_file.read()).decode('utf-8')

url = "http://localhost:11434/api/generate"
payload = {
    "model": "llava",
    "prompt": "describe this image",
    "images": [image_base64],
    "stream": False
}

# send post
response = requests.post(url, json=payload)  # use json parameter instead of data=json.dumps(payload)

print(response.text)  # print the response content
