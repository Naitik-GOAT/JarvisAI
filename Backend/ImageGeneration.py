import os
import requests
import base64
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv
from time import sleep

# Load Hugging Face API key from .env file
load_dotenv()
API_KEY = os.getenv("HuggingFaceAPIKey")
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

# Ensure the Data directory exists
os.makedirs("Data", exist_ok=True)

def query_sdxl(prompt: str) -> bytes:
    payload = {"inputs": prompt}
    response = requests.post(API_URL, headers=HEADERS, json=payload)
    
    if response.status_code == 200 and "image" in response.headers.get("content-type", ""):
        return response.content
    else:
        print(f"[Error] {response.status_code}: {response.text}")
        return None

def generate_images(prompt: str, count: int = 4):
    safe_prompt = prompt.replace(" ", "_").replace(",", "")
    for i in range(1, count + 1):
        print(f"Generating image {i}...")
        image_bytes = query_sdxl(prompt)
        if image_bytes:
            file_path = os.path.join("Data", f"{safe_prompt}{i}.jpg")
            with open(file_path, "wb") as f:
                f.write(image_bytes)
            print(f"Saved: {file_path}")
        else:
            print(f"Image {i} generation failed.")
        sleep(1)

def open_images(prompt):
    safe_prompt = prompt.replace(" ", "_").replace(",", "")
    for i in range(1, 5):
        file = os.path.join("Data", f"{safe_prompt}{i}.jpg")
        if os.path.exists(file):
            img = Image.open(file)
            img.show()
        else:
            print(f"Image not found: {file}")

def main():
    while True:
        try:
            with open(r"Frontend\Files\ImageGeneration.data", "r") as f:
                data = f.read().strip()
            
            # FIX: Allow prompt with commas by splitting on last comma
            parts = [x.strip() for x in data.rsplit(",", 1)]
            if len(parts) != 2:
                print(f"[Format Error] Invalid file format: {data}")
                sleep(1)
                continue

            prompt, status = parts
            if status.lower() == "true":
                print(f"Prompt: '{prompt}' | Status: '{status}'")
                generate_images(prompt)
                open_images(prompt)

                with open(r"Frontend\Files\ImageGeneration.data", "w") as f:
                    f.write("False,False")
                break
            else:
                sleep(1)
        except Exception as e:
            print(f"[Error] {e}")
            sleep(1)

if __name__ == "__main__":
    main()
