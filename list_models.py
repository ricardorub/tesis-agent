import os
from cerebras.cloud.sdk import Cerebras

# Use the API key from the user's file
CEREBRAS_API_KEY = "csk-rhecyfemftvk634p2dkhr95et56cj8hxxpy8njy3dd3mm9k8"

client = Cerebras(api_key=CEREBRAS_API_KEY)

try:
    # Most OpenAI-compatible SDKs have a models.list() method
    models = client.models.list()
    print("Available models:")
    for model in models.data:
        print(f"- {model.id}")
except Exception as e:
    print(f"Error listing models: {e}")
