import io
import os
import warnings
import random
import numpy as np
import requests
import pickle
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from PIL import Image
from gradio_client import Client

load_dotenv()

def text_to_image(prompt):
    client = InferenceClient(os.getenv("TEXT_TO_IMAGE_MODEL"), token=os.getenv("HUGGINGFACE_API_TOKEN"))
    # output is a PIL.Image object
    image = client.text_to_image(prompt)
    return image

