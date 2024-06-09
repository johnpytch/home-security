import PIL.Image
from home_security.model import load_model
from home_security.inference import inference
from typing import List


def test_load_model(test_image: PIL.Image):
    model, processor = load_model()
    assert model
    assert processor

    detections = inference(
        model=model, processor=processor, image=test_image, min_score=0.7
    )
    assert isinstance(detections, List)
    assert isinstance(detections[0]["score"], float)
    assert isinstance(detections[0]["label"], str)
    assert isinstance(detections[0]["box"], List)
    assert isinstance(detections[0]["box"][0], float)
    assert len(detections[0]["box"]) == 4
