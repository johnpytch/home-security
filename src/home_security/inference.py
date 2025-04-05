import torch
from typing import List, Dict, Tuple


def inference(model, processor, image, min_score) -> List[Dict[str, Tuple[str, float]]]:

    # Process the image and convert into a tensor
    inputs = processor(images=image, return_tensors="pt")

    # Forward pass through the nmodel
    outputs = model(**inputs)

    # Convert output results to original size
    target_sizes = torch.tensor([image.size[::-1]])

    # only keep detections with score >= min_score
    results = processor.post_process_object_detection(
        outputs, target_sizes=target_sizes, threshold=min_score
    )[0]

    # Loop through the results, creating a List[Dict] of detections that are 'person'
    detections = []
    for score, label, box in zip(
        results["scores"], results["labels"], results["boxes"]
    ):
        box = [round(i, 2) for i in box.tolist()]
        lab = model.config.id2label[label.item()]
        if lab in ["person"]:
            detections.append(
                {
                    "label": lab,
                    "score": round(score.item(), 2),
                    "box": box,
                }
            )
    return detections
