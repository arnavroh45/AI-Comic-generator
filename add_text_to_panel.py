# pylint: disable=too-many-locals
# pylint: disable=invalid-name
"""
This module provides functions to add text to a comic panel image.
"""
import textwrap
from PIL import Image, ImageDraw, ImageFont

def add_text_to_panel(text, panel_image):
    """
    Adds text to a comic panel image.

    Args:
        text (str): The text to add to the panel.
        panel_image (PIL.Image.Image): The comic panel image.

    Returns:
        PIL.Image.Image: The resulting image with the text added.
    """
    text_image = generate_text_image(text)

    result_image = Image.new('RGB', (panel_image.width, panel_image.height + text_image.height))

    result_image.paste(panel_image, (0, 0))

    result_image.paste(text_image, (0, panel_image.height))

    return result_image

def generate_text_image(text):
    """
    Generates an image with the given text.

    Args:
        text (str): The text to add to the image.

    Returns:
        PIL.Image.Image: The resulting image with the text added.
    """
    # Define image dimensions
    width = 1024
    height = 128

    # Create a white background image
    image = Image.new('RGB', (width, height), color='white')

    # Create a drawing context
    draw = ImageDraw.Draw(image)

    # Choose a font (Pillow's default font)
    font = ImageFont.truetype(font="manga-temple.ttf", size=30)   
    # Calculate text size
    text_width, text_height, text_length, text_breadth = draw.textbbox([width, height], text=text, font=font)

    # Calculate the new text size
    max_text_width = width - 20  # Add some margin
    avg_char_width = font.getbbox("A")[2]  # Approximate width of a character
    wrapped_text = textwrap.fill(text, width=int(max_text_width / avg_char_width))

    # Calculate the total height of the wrapped text to position it vertically
    text_height = sum(font.getbbox(line)[3] for line in wrapped_text.splitlines())

    x = 10
    y = (height - text_height) // 2

    # Define text color (black in this example)
    text_color = (0, 0, 0)

    # Add text to the image
    draw.multiline_text((x, y), wrapped_text, fill=text_color, font=font, spacing=4)


    return image
