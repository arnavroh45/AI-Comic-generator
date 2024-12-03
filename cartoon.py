# pylint: disable=line-too-long
import json
import time
import requests
from PIL import Image
from generate_panels import generate_panels
from stability_ai import text_to_image
from add_text_to_panel import add_text_to_panel
from comic_strip import create_strip 
from cloudinary_functions import upload_image_to_cloudinary

# ==========================================================================================
#inputs are scenario and style, kuch aur daalna hai voh bhi daal sakte hain
SCENARIO = """

Show that sahiba is born in a rich family in an Punjabi village

Show that mirza is born in a poor family in the same village

Both used to play together in the masjid. Their Punjabi teacher named Kazi, is not happy with them since they do not study and play together.

Sahiba went to a village shop wearing punjabi lehenga to get honey.

Karmu brahman went to danabad on horse to mirza to tell about Sahiba's marriage.

Mirza's dad encourages him to go and get sahiba for family honor since they were engaged in childhood.

Mirza rode his strong horse, to bibo massi (aunty) to village syal to so that she conveys message that mirza has arrived.

Bibo massi went to sahiba, who was sleeping and arranges the meeting with mirza.

Mirza and sahiba ran away riding his horse.

Mirza stops at a far distance to take rest under a tree.

Sahiba insists to continue the journey so they reach at mirza house at danabad.

Sahiba's punjabi brothers chased and found them. They fought with mirza and killed him with swords and arrows.
"""

STYLE = """
  Time: 400 years ago
  Place: Ancient Punjab, in a rural village setting with havelis, fields, and a masjid.
  Primary genre: Folktales
  Secondary genre: Romance
  """

panel_images = []
# ==========================================================================================

# print(f"Generate panels with style '{STYLE}' for this scenario: \n {SCENARIO}")
# panels = generate_panels(SCENARIO)

# with open('output/panels.json', 'w') as outfile:
#   json.dump(panels, outfile)

# with open('output/panels.json', 'r') as json_file:
#   panels = json.load(json_file)


def generate_image_with_retry(panel):
    """
    Generate an image for a given panel with retries in case of errors.

    Args:
        panel (dict): A dictionary containing panel details such as description, background, and number.

    Returns:
        Image: The generated image for the panel.
    """
    retries = 0
    max_retries = 5  # Maximum number of retries per panel
    wait_time = 300  # Wait time in seconds (5 minutes) if quota is exceeded

    while retries < max_retries:
        try:
            # Generate the image for the panel
            panel_prompt = panel["Description"] + panel["Background"] + ", cartoon box, " + STYLE
            print(f"Generating image for panel {panel['number']}...")

            # Call the function to generate the image
            image = text_to_image(panel_prompt)
            # image.save(f"output1_new2121/panel-{panel['number']}.png")
            # print(f"Panel {panel['number']} saved.")
            return image

        except Exception as e:
            retries += 1
            print(f"Error generating panel {panel['number']} (Attempt {retries}/{max_retries}): {e}")
            if "exceeded your GPU quota" in str(e):
                print(f"Quota exceeded. Waiting for {wait_time // 60} minutes before retrying...")
                time.sleep(wait_time)  # Wait 5 minutes
            else:
                print("Encountered a different error. Waiting for 75 seconds before retrying...", str(e))
                time.sleep(75)  # Short wait time for non-quota errors

    if retries == max_retries:
        print(f"Failed to generate panel {panel['number']} after {max_retries} attempts. Skipping.")

def create_batch_strip(user_id, comic_title, batch, batch_number):
    """
    Create a comic strip from a batch of panels and upload it to Cloudinary.

    Args:
        user_id (str): The ID of the user creating the comic strip.
        comic_title (str): The title of the comic strip.
        batch (list): A list of panel images to include in the strip.
        batch_number (int): The batch number for the strip.

    Returns:
        str: The URL of the uploaded comic strip.
    """
    strip = create_strip(batch)
    # strip.save(f"output1/strip-{batch_number}.png")
    strip_url = upload_image_to_cloudinary(strip, user_id, comic_title, batch_number)
    return strip_url


batch_size = 6

# for i, panel in enumerate(panels):
#     panel_image = generate_image_with_retry(panel)
#     if(panel["Text"]):
#       panel_image_with_text = add_text_to_panel(panel["Text"], panel_image)
#     else:
#         panel_image_with_text = panel_image
#     panel_image_with_text.save(f"output/panel-{panel['number']}.png")
#     panel_images.append(panel_image_with_text)
#     if len(panel_images) == batch_size:
#         create_batch_strip(panel_images, i // batch_size + 1)
#         panel_images.clear()

# if panel_images:
#     create_batch_strip(panel_images, len(panels) // batch_size + 1)




