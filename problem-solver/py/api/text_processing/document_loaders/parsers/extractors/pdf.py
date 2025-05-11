import json
import time

try:
    from pdfminer.high_level import extract_pages
    from pdfminer.layout import LTPage, LTComponent, LTTextContainer, LTCurve, LTImage, LTFigure
except ImportError:
    raise ImportError("pdfminer.six package not found, please install it with `pip install pdfminer.six`")

from ....objects import TextBlock, ImageBlock, BaseObject


class PDFMinerExtractor:
    """
    Extracts text and image objects from PDF files using PDFMiner.
    
    Processes PDF pages in batches for improved performance and memory usage.
    Extracts text blocks and image/figure elements while preserving their 
    bounding box coordinates and page numbers.
    """

    def __init__(self, batch_size: int = 50, print_logs: bool = False) -> None:
        """
        Initialize PDFMinerExtractor.
        
        Args:
            batch_size: Number of pages to process in each batch
            print_logs: Whether to print processing progress logs
        """
        self.batch_size = batch_size
        self.print_logs = print_logs

    def load(self, filepath: str) -> list[TextBlock | ImageBlock]:
        """
        Load and process a PDF file to extract text and image objects.
        
        Processes pages in batches defined by batch_size. Extracts text blocks
        and image elements while preserving their positioning information.
        
        Args:
            filepath: Path to the PDF file to process
            
        Returns:
            List of extracted TextBlock and ImageBlock objects
        """

        start_time = time.time()

        results = []
        pages_processed = 0
        current_batch = []
        prev_timer = time.time()

        # Iterate through pages and process them in batches
        for page in extract_pages(filepath):
            current_batch.append(page)
            pages_processed += 1

            if len(current_batch) >= self.batch_size:
                batch_results = []
                for p in current_batch:
                    batch_results.extend(self.extract_objects(p))
                results.extend(batch_results)
                if self.print_logs:
                    print(f"Processed {pages_processed} pages in {time.time() - prev_timer}")
                prev_timer = time.time()
                current_batch = []

        # Process remaining pages
        if current_batch:
            batch_results = []
            for p in current_batch:
                objects = [object for object in self.extract_objects(p) if object]
                batch_results.extend(objects)
            results.extend(batch_results)

        execution_time = time.time() - start_time
        if self.print_logs:
            print(f"Total {pages_processed} pages loaded in {execution_time:.2f} seconds.")
        return results

    def extract_objects(self, page: LTPage) -> list[TextBlock | ImageBlock]:
        """
        Extract text and image objects from a single PDF page.
        
        Processes each element on the page and creates corresponding TextBlock 
        or ImageBlock objects with positioning information.
        
        Args:
            page: PDFMiner LTPage object representing a PDF page
            
        Returns:
            List of TextBlock and ImageBlock objects found on the page
        """

        def extract(item: LTComponent, page_id: int):
            if isinstance(item, LTTextContainer):
                if item.get_text().replace(" ", "") == "\n":
                    pass
                else:
                    return TextBlock(
                        text=item.get_text(),
                        bbox=item.bbox,
                        page=page_id
                    )
            if isinstance(item, (LTCurve, LTImage, LTFigure)):
                if item.bbox[1]!=item.bbox[3] and item.bbox[0]!=item.bbox[2]:
                    return ImageBlock(bbox=item.bbox, page=page_id)
            return None

        objects = []
        for element in page:
            obj = extract(element, page.pageid)
            if obj:
                objects.append(obj)

        return objects

    def to_dict(self, obj):
        """
        Convert an object to a dictionary format for JSON serialization.
        
        Args:
            obj: Object to convert (TextBlock, ImageBlock or other)
            
        Returns:
            Dictionary representation of the object
        """
        if isinstance(obj, (TextBlock, ImageBlock)):
            return obj.__dict__
        if isinstance(obj, BaseObject):
            return obj.__dict__
        return str(obj)

    def save_to_json(self, objects, output_path):
        """
        Save extracted objects to a JSON file.
        
        Args:
            objects: List of objects to serialize
            output_path: Path where to save the JSON file
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(objects, f, default=self.to_dict, ensure_ascii=False, indent=2)
