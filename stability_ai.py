# pylint: disable=too-many-locals
# pylint: disable=missing-function-docstring
# pylint: disable=no-name-in-module
# pylint: disable=import-error
# pylint: disable=line-too-long
# pylint: disable=raise-missing-from

from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from config import TEXT_TO_IMAGE_MODEL, HUGGINGFACE_API_TOKEN

load_dotenv()

def text_to_image(prompt):
    client = InferenceClient(TEXT_TO_IMAGE_MODEL, token=HUGGINGFACE_API_TOKEN)
    # output is a PIL.Image object
    image = client.text_to_image(prompt)
    return image

