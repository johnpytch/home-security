from transformers import DetrImageProcessor, DetrForObjectDetection
import time


def load_model():
    print("Loading model...")
    start_time = time.time()
    processor = DetrImageProcessor.from_pretrained(
        "facebook/detr-resnet-50", revision="no_timm"
    )
    model = DetrForObjectDetection.from_pretrained(
        "facebook/detr-resnet-50", revision="no_timm"
    )
    end_time = time.time()
    print("Took {} seconds to load".format(end_time - start_time))
    return model, processor
