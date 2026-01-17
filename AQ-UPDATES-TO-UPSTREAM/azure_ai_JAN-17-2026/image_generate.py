
# Image Generation Script: Generates an image using Azure OpenAI and saves the result with a unique filename.

import os  # For environment variables
import requests  # For HTTP requests
import base64  # For decoding base64 image data
from PIL import Image  # For image processing
from io import BytesIO  # For handling image bytes
from azure.identity import DefaultAzureCredential  # For Azure authentication
import random  # For generating random strings
import string  # For generating random strings
from datetime import datetime  # For timestamping


# Azure OpenAI configuration
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "https://r2d2-foundry-001.openai.azure.com/")
deployment = os.getenv("DEPLOYMENT_NAME", "FLUX.1-Kontext-pro")
api_version = os.getenv("OPENAI_API_VERSION", "2025-04-01-preview")


# Generate a random string for unique filenames
def random_string(length=8):
  return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))


# Get a timestamp string for filenames
def get_timestamp():
  return datetime.now().strftime("%Y%m%d_%H%M%S")


# Decode a base64 image and save it to a file
def decode_and_save_image(b64_data, output_filename):
  image = Image.open(BytesIO(base64.b64decode(b64_data)))
  image.show()
  image.save(output_filename)


# Save the image from the API response with a unique, descriptive filename
def save_response(response_data, filename_prefix):
  if 'data' not in response_data:
    print("Error in response:", response_data)
    return
  data = response_data['data']
  b64_img = data[0]['b64_json']
  rand = random_string()
  timestamp = get_timestamp()
  filename = f"{filename_prefix}_{rand}_{timestamp}.png"
  decode_and_save_image(b64_img, filename)
  print(f"Image saved to: '{filename}'")


# Authenticate with Azure
credential = DefaultAzureCredential()
token_response = credential.get_token("https://cognitiveservices.azure.com/.default")


# Prepare API endpoint paths
base_path = f'openai/deployments/{deployment}/images'
params = f'?api-version={api_version}'


# Prepare the generation request
generation_url = f"{endpoint}{base_path}/generations{params}"
generation_body = {
  "prompt": "Earth from international space station",  # Generation prompt
  "n": 1,
  "size": "1024x1024",
  "output_format": "png"
}

# Send the generation request to Azure OpenAI and save the result
generation_response = requests.post(
  generation_url,
  headers={
    'Authorization': 'Bearer ' + token_response.token,
    'Content-Type': 'application/json',
  },
  json=generation_body
).json()
save_response(generation_response, "generated_image")
