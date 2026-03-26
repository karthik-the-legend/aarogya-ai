import sys
sys.path.insert(0, 'backend')

import os
import requests
from dotenv import load_dotenv
load_dotenv()

key = os.getenv('SARVAM_API_KEY', '')
print(f'Key found: {bool(key)} — starts with: {key[:8]}...')

response = requests.post(
    "https://api.sarvam.ai/translate",
    headers={"api-subscription-key": key},
    json={
        "input"                : "I have fever",
        "source_language_code" : "en-IN",
        "target_language_code" : "hi-IN",
        "mode"                 : "formal",
        "model"                : "mayura:v1"
    },
    timeout=10
)

print(f'Status code : {response.status_code}')
print(f'Response    : {response.text}')