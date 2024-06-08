from transformers import DetrImageProcessor, DetrForObjectDetection
import time
import logging


def load_model():
    logging.info("Loading model...")
    start_time = time.time()
    processor = DetrImageProcessor.from_pretrained(
        "facebook/detr-resnet-50", revision="no_timm"
    )
    model = DetrForObjectDetection.from_pretrained(
        "facebook/detr-resnet-50", revision="no_timm"
    )
    end_time = time.time()
    logging.info(f"Took {end_time - start_time} seconds to load")
    return model, processor
