from PIL import ImageDraw, Image
from typing import List, Dict


def annotate_detections(image: Image, detections: List[Dict]) -> Image:
    """
    Given an image and detections, annotate the image with the detection boxes

    Args:
        image (PIL.Image): The image to annotate
        detections (List[Dict]): The detections to annotate

    Returns:
        Image: The annotated image
    """

    # Annotate image only with detections of people
    for det in detections:
        if det["label"] in ["person"]:
            bounding_box = ImageDraw.Draw(image)
            bounding_box.rectangle(det["box"], outline="red", width=1)

    return image
