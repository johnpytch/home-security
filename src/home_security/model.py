import tensorflow as tf
from object_detection.utils import label_map_util
import time
from src.home_security.settings import NUM_CLASSES, PATH_TO_LABELS, PATH_TO_SAVED_MODEL


def load_model():
    tf.get_logger().setLevel("ERROR")
    label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
    categories = label_map_util.convert_label_map_to_categories(
        label_map, max_num_classes=NUM_CLASSES, use_display_name=True
    )
    category_index = label_map_util.create_category_index(categories)
    print("Loading model...")
    start_time = time.time()
    model = tf.saved_model.load(PATH_TO_SAVED_MODEL)
    end_time = time.time()
    print("Took {} seconds to load".format(end_time - start_time))
    return model, category_index
