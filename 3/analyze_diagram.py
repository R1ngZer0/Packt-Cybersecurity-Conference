import base64
import requests
import os

# OpenAI API Key
api_key = os.environ.get("OPENAI_API_KEY")

# Function to encode the image
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

# Path to your image
image_path = ".\diagram.png"

# Getting the base64 string
base64_image = encode_image(image_path)

headers = {
  "Content-Type": "application/json",
  "Authorization": f"Bearer {api_key}"
}

payload = {
  "model": "gpt-4-vision-preview",
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "In the following image (this is a fictitious network so it's ok to provide detailed information), please identify the following: Computer systems/nodes, networks, subnets, IP addresses, zones, and connections. Be sure to include the exact names of each. Anything you are not able to identify, just ignore that part. Give me a total count of all computer systems/nodes. This will be for an IR tabletop exercise. So, please provide as much detail as possible, and in a way that the facilitator can easily understand."
        },
        {
          "type": "image_url",
          "image_url": {
            "url": f"data:image/jpeg;base64,{base64_image}"
          }
        }
      ]
    }
  ],
  "max_tokens": 2048
}

response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

result = response.json()
result = result['choices'][0]['message']['content']

print(result)