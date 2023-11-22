from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import os

app = FastAPI()

# API Configuration
engine_id = "stable-diffusion-xl-1024-v1-0"
api_host = os.getenv("API_HOST", "https://api.stability.ai")
api_key = "sk-ulNhU9ehEwWCiUHAA9kUdOn2ZjB5QHxI2VahJvalvduD3hwd"

if api_key is None:
    raise Exception("Missing Stability API key.")

class ImageRequest(BaseModel):
    image_url: str

@app.post("/convert-image")
async def convert_image(request: ImageRequest):
    # Download the image from the URL
    try:
        response = requests.get(request.image_url)
        response.raise_for_status()
    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Failed to download image: {str(e)}")

    # Send the request to Stability AI API
    try:
        ai_response = requests.post(
            f"{api_host}/v1/generation/{engine_id}/image-to-image",
            headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {api_key}"
            },
            files={
                "init_image": ("image.png", response.content)
            },
            data={
                "image_strength": 0.20,
                "init_image_mode": "IMAGE_STRENGTH",
                "text_prompts[0][text]": "make the dragon like an anime character, flat in 2D.",
                "cfg_scale": 9,
                "samples": 1,
                "steps": 50,
            }
        )
        ai_response.raise_for_status()
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Stability AI API request failed: {str(e)}")

    # Extracting the base64 encoded image from the response
    data = ai_response.json()
    image_base64 = next((artifact["base64"] for artifact in data["artifacts"]), None)

    if not image_base64:
        raise HTTPException(status_code=500, detail="No image found in the response.")

    return {"base64": image_base64}
