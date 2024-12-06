"""
This module provides API endpoints for generating and editing comic strips.
"""

# pylint: disable=too-many-locals
# pylint: disable=missing-function-docstring
# pylint: disable=no-name-in-module
# pylint: disable=import-error
# pylint: disable=line-too-long
# pylint: disable=raise-missing-from

import os
import json
import base64
import asyncio
from urllib.parse import urlparse
from io import BytesIO
import cloudinary
import cloudinary.uploader
import cloudinary.api
import requests
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from PIL import Image
from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends
from pymongo import MongoClient

# Importing your existing functions
from add_text_to_panel import add_text_to_panel
from cloudinary_functions import upload_image_to_cloudinary
from models import ComicRequest, EditImage
from cartoon import generate_image_with_retry, create_batch_strip
from generate_panels import generate_panels
from stability_ai import text_to_image
from config import SEGMIND_API_KEY, SEGMIND_URL, CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET, db, users, comics
from jwt_utils import get_current_user

load_dotenv()
cloudinary.config(
    cloud_name = CLOUDINARY_CLOUD_NAME,
    api_key = CLOUDINARY_API_KEY,
    api_secret = CLOUDINARY_API_SECRET,
    secure=True
)

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")



def image_url_to_base64(image_url):
    response = requests.get(image_url)
    image_data = response.content
    return base64.b64encode(image_data).decode('utf-8')

# API endpoint to generate the comic strip
@app.post("/generate_comic/")
async def generate_comic(request: ComicRequest, user : dict = Depends(get_current_user)):
    if not request.scenario or not request.style:
        raise HTTPException(status_code=400, detail="Both 'scenario' and 'style' are required.")
    try:
        userdata = users.find_one({"email": user.get('email')})
        if not userdata:
            raise HTTPException(status_code=404, detail="User not found")
        user_id = userdata['uid']
        if not user_id:
            raise HTTPException(status_code=404, detail="User ID not found")

        comic_title = request.title

        # Generate panels from the scenario
        panels = generate_panels(request.scenario, request.template)
        panels_path = f"{user_id}_comic/{comic_title}/panels"
        json_data = json.dumps(panels)
        json_bytes = BytesIO(json.dumps(json_data).encode('utf-8'))
        response = cloudinary.uploader.upload(
            json_bytes,
            resource_type = "raw",
            public_id = panels_path,
            format = "json"
        )
        file_response = cloudinary.api.resource(f"{panels_path}.json", resource_type="raw")
        file_url = file_response['url']
        response = requests.get(file_url)
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to fetch JSON file from Cloudinary")
        panels = response.json()  # Correct approach to parse JSON
        if isinstance(panels, str):  # Handle edge case where JSON is a string
            panels = json.loads(panels)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during setup or panel generation: {str(e)}")

    try:
        panel_images = []
        image_links = []
        strip_links = []
        batch_size = 6


        # with open('output1/panels.json', 'w') as outfile:
        #     json.dump(panels, outfile)

        # with open('output1/panels.json', 'r') as json_file:
        #     panels = json.load(json_file)

        for i, panel in enumerate(panels):
            panel_image = generate_image_with_retry(panel)
            if panel["Text"]:
                panel_image_with_text = add_text_to_panel(panel["Text"], panel_image)
            else:
                panel_image_with_text = panel_image

            panel_url = upload_image_to_cloudinary(panel_image_with_text, user_id, comic_title, panel['number'])
            # panel_image_with_text.save(f"output1/panel-{panel['number']}.png")

            image_links.append(panel_url)
            panel_images.append(panel_image_with_text)
            if len(panel_images) == batch_size:
                strip_url = create_batch_strip(user_id, comic_title, panel_images, i // batch_size + 1)
                strip_links.append(strip_url)
                panel_images.clear()

        if panel_images:
            strip_url = create_batch_strip(user_id, comic_title, panel_images, len(panels) // batch_size + 1)
            strip_links.append(strip_url)

        document = {
            "user_id": user_id,
            "title": comic_title,
            "scenario": request.scenario,
            "style": request.style,
            "images_links": image_links,
            "strip_links": strip_links
        }
        comics.insert_one(document)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing panels or generating images: {str(e)}")

        # Return the URLs of generated strips
    return {
        "message": "Comic generation successful.",
        "strips": "Done",
    }

# API endpoint to get the generated comic strip
@app.get("/get_comic/{comic_title}")
async def get_comic(comic_title: str,  user : dict = Depends(get_current_user)):
    userdata = users.find_one({"email": user.get('email')})
    if not userdata:
        raise HTTPException(status_code=404, detail="User not found")
    user_id = userdata['uid']
    if not user_id:
        raise HTTPException(status_code=404, detail="User ID not found")
    comic = await comics.find_one({"user_id": user_id, "title": comic_title})
    if not comic:
        raise HTTPException(status_code=404, detail="Comic not found")

    return {
        "image_links": comic.get("images_links", []),
        "strip_links": comic.get("strip_links", []),
    }

@app.post("/edit_image/{image_url}")
async def edit_image(image_url: str, request: EditImage):
    parsed_url = urlparse(image_url)
    path = parsed_url.path
    path_parts = path.split('/')
    combined_title = path_parts[-3]  # "123_comic"
    panel_number = path_parts[-1].split('.')[0]
    user_id, comic_title = combined_title.split('_')  # Splitting "123_comic"

    # client = Client("multimodalart/cosxl")
    try:
        # result = await asyncio.to_thread(
        # client.predict,
        # image=handle_file(request.image_url),
        # prompt=request.prompt,
        # negative_prompt="",
		# guidance_scale=7,
		# steps=20,
		# api_name="/run_edit"
        # )
        data = {
            "prompt": request.prompt,
            "image": image_url_to_base64(request.image_url),  # Or use image_file_to_base64("IMAGE_PATH")
            "steps": 20,
            "seed": 46588,
            "denoise": 0.75,
            "scheduler": "simple",
            "sampler_name": "euler",
            "base64": False
        }
        headers = {'x-api-key': SEGMIND_API_KEY}
        response = requests.post(SEGMIND_URL, json=data, headers=headers)
        image_data = response.content
        edited_image = Image.open(BytesIO(image_data))
        panel_url = upload_image_to_cloudinary(edited_image, user_id, comic_title, panel_number+"edited")
        return {"panel_url":panel_url}
        # panel_url = upload_image_to_cloudinary(response.content, user_id, comic_title, panel['number'])
    except asyncio.CancelledError:
        # Handle client disconnectionos
        print("Request was cancelled by the client.")
        raise HTTPException(status_code=499, detail="Request cancelled by the client.")
    except Exception as e:
        # General exception handling
        raise HTTPException(status_code=500, detail=str(e))
