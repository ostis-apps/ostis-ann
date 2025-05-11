try:
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    from matplotlib.collections import PatchCollection
except ImportError:
    raise ImportError(
        "Could not import matplotlib. Please install it with 'pip install matplotlib'"
    )


def visualize_objects(objects, img_size=(460, 640), thickness=2):
    if 'plt' not in globals():
        raise ImportError(
            "Matplotlib is required for visualization. Please install it with 'pip install matplotlib'"
        )
    """
    Visualizes a list of objects on a 2D plot with distinct bounding boxes and colors.
    Each type of object is represented by a unique color, with options to highlight
    nested objects and captions within the main object bounds.

    :param objects: A list of objects to be visualized. Each object must have the
        attributes `type`, `bbox`, and optionally `text_blocks` and `caption`.
        - `type`: The type of the object (e.g., 'text', 'image').
        - `bbox`: A tuple containing the bounding box coordinates (x1, y1, x2, y2).
        - `text_blocks`: Nested objects each with their own `bbox`.
        - `caption`: Optional caption object with its own `bbox`.

    :param img_size: A tuple specifying the size of the image/page dimensions
        in the form `(width, height)`. Default is (460, 640).

    :param thickness: An integer specifying the line thickness for the bounding
        boxes. Default is 2.

    :return: None. Displays a visualization plot of the objects.
    """
    plt.figure(figsize=(8, 12))
    ax = plt.gca()

    page_rect = Rectangle((0, 0), img_size[0], img_size[1], facecolor='black', alpha=0.1)
    ax.add_patch(page_rect)

    color_map = {
        'text': 'blue',
        'image': 'red',
        'image_caption': 'orange',
        'table': 'green',
        'header': 'purple',
        'image_text': 'violet'
    }

    for type_name in color_map:
        main_patches = []
        nested_patches = []
        caption_patches = []

        for obj in objects:
            if hasattr(obj, 'type') and obj.type == type_name and obj.bbox:
                x1, y1, x2, y2 = obj.bbox
                width = x2 - x1
                height = y2 - y1
                main_patches.append(Rectangle((x1, y1), width, height, fill=False))

                # Обрабатываем вложенные объекты для всех типов блоков
                if hasattr(obj, 'text_blocks') and obj.text_blocks:
                    for nested_obj in obj.text_blocks:
                        if hasattr(nested_obj, 'bbox'):
                            x1, y1, x2, y2 = nested_obj.bbox
                            width = x2 - x1
                            height = y2 - y1
                            nested_patches.append(Rectangle((x1, y1), width, height, fill=False))

                if hasattr(obj, 'caption') and obj.caption and hasattr(obj.caption, 'bbox'):
                    x1, y1, x2, y2 = obj.caption.bbox
                    width = x2 - x1
                    height = y2 - y1
                    caption_patches.append(Rectangle((x1, y1), width, height, fill=False))

        if main_patches:
            collection = PatchCollection(
                main_patches, 
                facecolors='none',
                edgecolors=[color_map[type_name]],
                linewidth=thickness
            )
            ax.add_collection(collection)
            
        if nested_patches:
            nested_collection = PatchCollection(
                nested_patches,
                facecolors='none',
                edgecolors=['violet'],
                linewidth=thickness
            )
            ax.add_collection(nested_collection)

        if caption_patches:
            caption_collection = PatchCollection(
                caption_patches,
                facecolors='none',
                edgecolors=['orange'],
                linewidth=thickness
            )
            ax.add_collection(caption_collection)

    ax.set_xlim(0, img_size[0])
    ax.set_ylim(0, img_size[1])
    ax.set_aspect('equal')
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.set_xlabel('Width')
    ax.set_ylabel('Height')
    
    legend_elements = [plt.Line2D([0], [0], color=color, label=type_name.capitalize())
                      for type_name, color in color_map.items()]
    ax.legend(handles=legend_elements)
    
    plt.show()