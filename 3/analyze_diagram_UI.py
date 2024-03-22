import base64
import streamlit as st
import requests
import os

# OpenAI API Key
api_key = os.environ.get("OPENAI_API_KEY")

# Function to encode the image
def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

# Streamlit file uploader
image_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])
if image_file is not None:
    # Getting the base64 string
    base64_image = encode_image(image_file)
    # Streamlit text input for user prompt
    user_prompt = st.text_area("Enter your prompt", height=150)
    if user_prompt:
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
                            "text": user_prompt
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
        # Display the result
        st.write(result)