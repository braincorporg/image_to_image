from fastapi import FastAPI, HTTPException
import requests
import os

app = FastAPI()

@app.post("/transform-image/")
async def transform_image(image_url: str):
    # Download the image from the URL
    try:
        response = requests.get(image_url)
        response.raise_for_status()
        image_bytes = response.content
    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Failed to download image: {e}")

    # Prepare the request for the Stability AI API
    api_host = "https://api.stability.ai"
    api_key = "sk-ulNhU9ehEwWCiUHAA9kUdOn2ZjB5QHxI2VahJvalvduD3hwd"  # Replace with your actual API key
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    data = {
        "image_strength": 0.20,
        "init_image_mode": "IMAGE_STRENGTH",
        "text_prompts[0][text]": "make the dragon like an anime character, flat in 2D.",
        "cfg_scale": 9,
        "samples": 1,
        "steps": 50,
    }
    files = {
        "init_image": ("image.png", image_bytes, 'image/png')  # Using image_bytes directly
    }

    # Send request to Stability AI API
    try:
        stability_response = requests.post(
            f"{api_host}/v1/generation/stable-diffusion-xl-1024-v1-0/image-to-image",
            headers=headers,
            data=data,
            files=files
        )
        stability_response.raise_for_status()
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Stability AI API request failed: {e}")

    # Extract the base64 encoded image from the response
    stability_data = stability_response.json()
    base64_image = stability_data["artifacts"][0]["base64"]

    return {"base64_image": base64_image}

# Add other routes and logic as needed
