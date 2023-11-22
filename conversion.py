from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import base64
import os

app = FastAPI()

class ImageRequest(BaseModel):
    image_url: str
    text_prompt: str

# API Configuration
engine_id = "stable-diffusion-xl-1024-v1-0"
api_host = os.getenv("API_HOST", "https://api.stability.ai")
api_key = "sk-ulNhU9ehEwWCiUHAA9kUdOn2ZjB5QHxI2VahJvalvduD3hwd"

if not api_key:
    raise Exception("Missing Stability API key.")

@app.post("/convert-image/")
async def convert_image(request: ImageRequest):
    # Download the image from the URL
    response = requests.get(request.image_url)
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to download image")

    # Prepare and send the request using the image bytes
    ai_response = requests.post(
        f"{api_host}/v1/generation/{engine_id}/image-to-image",
        headers={
            "Accept": "application/json",
            "Authorization": f"Bearer {api_key}"
        },
        files={
            "init_image": ("image.png", response.content)  # Pass image bytes directly
        },
        data={
            "image_strength": 0.20,
            "init_image_mode": "IMAGE_STRENGTH",
            "text_prompts[0][text]": request.text_prompt,
            "cfg_scale": 9,
            "samples": 1,
            "steps": 50,
        }
    )

    # Check the AI response
    if ai_response.status_code != 200:
        raise HTTPException(status_code=500, detail="Error processing image with AI")

    # Process the AI response
    ai_data = ai_response.json()
    base64_encoded_image = ai_data["artifacts"][0]["base64"]

    return {"base64": base64_encoded_image}
