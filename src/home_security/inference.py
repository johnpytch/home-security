import tensorflow as tf
from object_detection.utils import visualization_utils as viz_utils
import numpy as np


def inference(model, category_index, image_np, min_score):
    input_tensor = tf.convert_to_tensor(image_np)
    input_tensor = input_tensor[tf.newaxis, ...]
    detections = model(input_tensor)

    num_detections = int(detections.pop("num_detections"))
    detections = {
        key: value[0, :num_detections].numpy() for key, value in detections.items()
    }
    detections["num_detections"] = num_detections
    detections["detection_classes"] = detections["detection_classes"].astype(np.int64)

    # remove unwanted detections
    detection_classes = []
    detection_boxes = []
    detection_scores = []
    det = []
    detection = {}
    for i in range(0, len(detections["detection_classes"])):
        if category_index.get(detections["detection_classes"][i]) != None:
            detection_classes.append(detections["detection_classes"][i])
            detection_boxes.append(detections["detection_boxes"][i])
            detection_scores.append(detections["detection_scores"][i])
    detection["detection_classes"] = np.array(detection_classes)
    detection["detection_scores"] = np.array(detection_scores)
    detection["detection_boxes"] = np.array(detection_boxes)
    detection["num_detections"] = np.array(len(detection_classes))

    image_np_with_detections = image_np.copy()
    viz_utils.visualize_boxes_and_labels_on_image_array(
        image_np_with_detections,
        detection["detection_boxes"],
        detection["detection_classes"],
        detection["detection_scores"],
        category_index,
        use_normalized_coordinates=True,
        max_boxes_to_draw=100,
        min_score_thresh=min_score,
        agnostic_mode=False,
        line_thickness=1,
    )
    for i in range(len(detection["detection_classes"])):
        if detection["detection_scores"][i] > min_score:
            print(
                "Detected {}".format(
                    category_index.get(detection["detection_classes"][i])["name"]
                )
            )
            det.append(category_index.get(detection["detection_classes"][i])["name"])
    return (image_np_with_detections, det)
