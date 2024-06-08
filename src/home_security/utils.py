def get_datetime(image_path: str):
    """
    Given an image path, extract the date and time the image was captured and convert to DateTime

    Args:
        image_path (str): The path to the image

    Returns:
        datetime: The datetime the image was captured
    """

    datetime = (
        image_path.split("/")[4].split("_")[1].split(".")[0][8:10]
        + ":"
        + image_path.split("/")[4].split("_")[1].split(".")[0][10:12]
        + " "
        + image_path.split("/")[4].split("_")[1].split(".")[0][6:8]
        + "-"
        + image_path.split("/")[4].split("_")[1].split(".")[0][4:6]
        + "-"
        + image_path.split("/")[4].split("_")[1].split(".")[0][0:4]
    )
    return datetime
