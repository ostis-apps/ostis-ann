import re
from typing import List

from ....objects import Block, ImageBlock, TextBlock, ImageCaption, Header


class ObjectsClassifier:
    """
    Handles the classification of different objects into structured categories,
    such as grouping text blocks with corresponding image blocks and processing
    image captions. It processes objects page by page, ensuring proper alignment
    and restructuring as needed for further usage.

    The main purpose of this class is to identify specific relationships between
    objects (e.g., text blocks, image blocks) and reorganize them into a
    structured and meaningful order.

    :ivar image_caption_regex: Precompiled regular expression to identify figure
        and image captions based on specific text formatting patterns.
    """

    def __init__(self):
        self.image_caption_regex = r"^(Рис\.|Рисунок|Figure|Fig(\.)*)\s(([0-9])*\.*)*"

    def classify(self, objects: List[Block]):
        """
        Classifies a list of block objects based on their page attribute, processes pages
        containing blocks by grouping them together, sorting them by their vertical position,
        and passing them to a processing method. The resulting processed objects are then
        returned in a flat list.

        :param objects: List of Block objects. Each object should have a `page` attribute
            indicating the page number, along with a `bbox` attribute defining its bounding
            box.
        :type objects: List[Block]
        :return: List of processed block objects after sorting and processing by page.
        :rtype: List[Block]
        """
        processed_objects = []
        page: int = objects[0].page
        page_objects = []
        for obj in objects:
            if obj.page == page:
                page_objects.append(obj)
            else:
                page_objects.sort(key=lambda obj: obj.bbox[3])
                page_objects.reverse()
                processed_objects.extend(self.process_page(page_objects))
                page_objects = [obj]
                page = obj.page
        processed_objects.extend(self.process_page(page_objects))
        return processed_objects

    def process_page(self, page_objects: List[Block]) -> List[Block]:
        """
        Processes a list of page objects by restructuring them into a sequence that
        associates related images, captions, and text blocks, while preserving an
        organized order based on their bounding box positions.

        :param page_objects: A list of Block objects representing elements on a page
                             (e.g., text, images, captions). The method processes and
                             filters this list based on relationships between objects.
        :return: A list of Block objects, including restructured and sorted page
                 elements. Items such as images, associated captions, and text blocks
                 are grouped logically in the returned structure.
        """
        restructured_objects = []

        images = self.find_images(page_objects)
        skip_ids = [image.id for image in images]
        skip_ids.extend([image.caption.id for image in images if image.caption])
        remove_ids = []

        for obj in page_objects:
            if obj.id in skip_ids:
                continue
            if images:
                for image in images:
                    if type(obj) == TextBlock:
                        if self._is_text_belong_to_image(obj, image):
                            image.text_blocks.append(obj)
                            skip_ids.append(obj.id)
                            remove_ids.append(obj.id)

            restructured_objects.append(obj)
        restructured_objects.extend(images)
        restructured_objects.sort(key=lambda obj: obj.bbox[3])
        restructured_objects.reverse()
        page_header, ids_to_remove = self.define_page_header(restructured_objects)
        if ids_to_remove:
            ids_to_remove.extend(remove_ids)
        else:
            ids_to_remove = remove_ids

        if page_header:
            restructured_objects = [obj for obj in restructured_objects if obj.id not in ids_to_remove]
            restructured_objects.insert(0, page_header)

        return restructured_objects

    def define_page_header(self, page_object: List[Block]):
        first_text_block = None
        merged_ids = []
        for obj in page_object:
            if isinstance(obj, TextBlock):
                first_text_block = obj
                break
        if first_text_block:
            page_header = []
            for obj in page_object:
                if isinstance(obj, TextBlock):
                    if (first_text_block.bbox[3] >= obj.bbox[1] >= first_text_block.bbox[1]
                            or first_text_block.bbox[3] >= obj.bbox[3] >= first_text_block.bbox[1] or
                            obj.bbox[3] >= first_text_block.bbox[1] >= obj.bbox[1]):
                        page_header.append(obj)
            if page_header:
                is_header = False
                for it in [re.match(r"(\d+\s+.*\n*$)|(^.*\d+\n$)", obj.text) for obj in page_header]:
                    if it is not None:
                        if re.match(r"Глава \d+\n", it.string):
                            is_header = False
                        else:
                            is_header = True
                        break

                if is_header:
                    page_header.sort(key=lambda item: item.bbox[3])
                    page_header.reverse()
                    merged_ids = [obj.id for obj in page_header]
                    page_header = Header(
                        id=first_text_block.id,
                        page=first_text_block.page,
                        bbox=
                        (
                            min(obj.bbox[0] for obj in page_header),
                            min(obj.bbox[1] for obj in page_header),
                            max(obj.bbox[2] for obj in page_header),
                            max(obj.bbox[3] for obj in page_header)
                        ),
                        text=' '.join(obj.text for obj in page_header if hasattr(obj, 'text'))
                    )
                    page_header.text.replace('\n', ' ')
                    page_header.text.replace('\t', ' ')
                    page_header.text.replace('  ', ' ')
                else:
                    return None, None
        else:
            return None, None
        return page_header, merged_ids

    def find_images(self, page_objects: List[Block]) -> List[ImageBlock]:
        """
        Find and return a list of image blocks from the given list of page objects. An image block
        is considered valid if it meets specific criteria based on its bounding box. Additionally,
        associate captions to the nearest preceding image block, if applicable. The function relies
        on the `image_caption_regex` to identify potential captions among textual elements.

        :param page_objects: A list of objects representing elements on a page, which may include
            image blocks, text, and other types of content.
        :returns: A list of `ImageBlock` objects where each object represents a valid identified
            image block with potentially associated captions.
        """
        image_blocks = []
        for obj in page_objects:
            if isinstance(obj, ImageBlock):
                if obj.bbox[3] - obj.bbox[1] > 4:
                    image_blocks.append(obj)
        ignore_ids = []
        for obj in page_objects:
            if hasattr(obj, 'text') and re.match(self.image_caption_regex, obj.text):
                nearest_image = self._find_nearest_image_before(obj, image_blocks)
                if nearest_image:
                    image_caption = ImageCaption()
                    image_caption.id = obj.id
                    image_caption.page = obj.page
                    image_caption.bbox = obj.bbox
                    image_caption.text = obj.text
                    nearest_image.caption = image_caption
        return image_blocks

    def _find_nearest_image_before(self, obj: TextBlock, images: List[ImageBlock]) -> ImageBlock:
        """
        Finds the nearest image positioned above a given text block.

        This function iterates over a list of image blocks and determines the closest
        image, based on vertical distance, that appears above the provided text block.
        If no such image exists, the function returns None.

        :param obj: The text block for which the nearest image above it is to be found.
            Must contain a bounding box (bbox) attribute.
        :param images: A list of image blocks to be checked. Each image block
            must contain a bounding box (bbox) attribute.
        :return: The nearest image block positioned above the given text block,
            or None if no such image exists.
        """
        nearest_image = None
        nearest_distance = float('inf')

        for image in images:
            if image.bbox[1] > obj.bbox[3]:  # Image is above text
                distance = image.bbox[1] - obj.bbox[3]
                if distance < nearest_distance:
                    nearest_distance = distance
                    nearest_image = image

        return nearest_image

    def _is_text_belong_to_image(self, obj: TextBlock, image: ImageBlock, vertical_threshold=4) -> bool:
        """
        Determines if a given text block belongs within the spatial boundary or
        context of a specified image block. The decision is based on positional
        relationships between the bounding boxes of the text block and the image
        block, as well as proximity thresholds vertically.

        :param obj: The text block being evaluated. It must include positional
            bounding box data.
        :param image: The image block to which the association is being checked.
            It must include positional bounding box data and optionally a caption.
        :param vertical_threshold: The vertical distance threshold used to determine
            proximity of the text block to the bottom of the image block. Default
            value is 4.
        :return: A boolean indicating whether the text block belongs to the image
            block contextually or spatially.
        """
        if image.bbox[1] <= obj.bbox[1] <= image.bbox[3]:
            return True
        if image.bbox[1] <= obj.bbox[3] <= image.bbox[3]:
            return True
        if image.caption:
            if image.caption.bbox[1] <= obj.bbox[1] <= image.bbox[3]:
                return True
        if 0 < obj.bbox[1] - image.bbox[3] < vertical_threshold:
            return True
        return False
