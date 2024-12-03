import cloudinary
import cloudinary.uploader
import cloudinary.api
import requests
from io import BytesIO
def upload_image_to_cloudinary(image, user_id, comic_title, panel_number):
    # Convert the PIL image to bytes
    image_bytes = BytesIO()
    image.save(image_bytes, format='PNG')
    image_bytes.seek(0)

    # Upload to Cloudinary
    response = cloudinary.uploader.upload(
        image_bytes,
        folder=f"{user_id}_comic/{comic_title}",  # Folder structure: user1_comic/comic_title/
        public_id=f"panel_{panel_number}",        # Unique name for the panel image
        resource_type="image",
        format="png"
    )
    return response['url']

def upload_text_to_cloudinary(text_file, user_id, comic_title, panel_number):
    # Upload the text to Cloudinary
    response = cloudinary.uploader.upload(
        text_file,
        folder=f"{user_id}_comic/{comic_title}",  # Folder structure
        public_id=f"panel_text_{panel_number}",  # Unique ID for the file
        resource_type="raw"  # Specify raw file type for text data
    )
    return response['url']

def read_text_from_cloudinary(file_url):
    # Fetch the content of the file from Cloudinary using the file URL
    response = requests.get(file_url)
    text_content = response.text  # Get the content as text
    return text_content
