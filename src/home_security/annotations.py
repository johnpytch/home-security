import matplotlib.pyplot as plt


def annotate_detections(image, detections):

    fig = plt.figure(figsize=(4.33, 3.66))
    plt.imshow(image, interpolation="nearest")
    plt.axis("off")
    ax = plt.gca()
    ax.set_axis_off()
    ax.spines["left"].set_visible(False)

    for det in detections:
        if det["label"] in ["person", "dog"]:
            (xmin, ymin, xmax, ymax) = det["box"]
            x_label = det["box"][0]
            y_label = det["box"][1]
            ax.add_patch(
                plt.Rectangle(
                    (xmin, ymin),
                    xmax - xmin,
                    ymax - ymin,
                    fill=False,
                    color="red",
                    linewidth=0.5,
                )
            )
            ax.annotate(
                f"{det['label']}: {det['score']*100}%",
                (x_label + 25, y_label - 10),
                color="white",
                fontsize=10,
                ha="center",
                va="center",
            )
    return fig
