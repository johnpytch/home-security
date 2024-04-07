import torch


def inference(model, processor, image, min_score):

    inputs = processor(images=image, return_tensors="pt")
    outputs = model(**inputs)

    # convert outputs (bounding boxes and class logits) to COCO API
    # let's only keep detections with score > 0.9
    target_sizes = torch.tensor([image.size[::-1]])
    results = processor.post_process_object_detection(
        outputs, target_sizes=target_sizes, threshold=min_score
    )[0]

    detections = []
    for score, label, box in zip(
        results["scores"], results["labels"], results["boxes"]
    ):
        box = [round(i, 2) for i in box.tolist()]
        lab = model.config.id2label[label.item()]
        if lab in ["person", "dog"]:
            detections.append(
                {
                    "label": lab,
                    "score": round(score.item(), 2),
                    "box": box,
                }
            )
            print(f"Detected {lab} with confidence " f"{round(score.item(), 2)}")
    return detections
