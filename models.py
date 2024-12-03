# pylint: disable=too-few-public-methods
# pylint: disable=missing-class-docstring
# pylint: disable=no-name-in-module
# Model for inputs

from pydantic import BaseModel

class ComicRequest(BaseModel):
    user_id: str
    title: str
    scenario: str
    style: str
    template: str

class EditImage(BaseModel):
    image_url: str
    prompt: str
