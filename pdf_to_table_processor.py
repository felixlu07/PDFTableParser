import os
import json
import csv
import shutil
from datetime import datetime
from pdf2image import convert_from_path
import base64
from io import BytesIO
import anthropic
from PIL import Image
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
OUTPUT_DIR = "output"
TEMP_DIR = "temp"

def ensure_directories():
    """Ensure output and temp directories exist."""
    for directory in [OUTPUT_DIR, TEMP_DIR]:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"Ensured directory exists: {directory}")

def cleanup_temp_files(temp_folder):
    """Clean up temporary files after processing."""
    try:
        if os.path.exists(temp_folder):
            shutil.rmtree(temp_folder)
            logger.info(f"Cleaned up temporary folder: {temp_folder}")
    except Exception as e:
        logger.warning(f"Error cleaning up temporary files: {e}")

def setup_anthropic_client():
    """Initialize Anthropic client with API key from environment."""
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
    try:
        return anthropic.Anthropic(api_key=api_key)
    except Exception as e:
        logger.error(f"Failed to initialize Anthropic client: {e}")
        raise

def convert_pdf_to_images(pdf_path, dpi=300):
    """Convert PDF to high-resolution images."""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_folder = os.path.join(TEMP_DIR, f"pdf_images_{timestamp}")
        os.makedirs(temp_folder, exist_ok=True)
        
        images = convert_from_path(
            pdf_path,
            dpi=dpi,
            fmt='jpeg',
            jpegopt={
                'quality': 95,
                'progressive': True,
                'optimize': True
            }
        )
        
        image_paths = []
        for i, image in enumerate(images):
            image_path = os.path.join(temp_folder, f"page_{i+1}.jpg")
            image.save(image_path, 'JPEG')
            image_paths.append(image_path)
            
        logger.info(f"Successfully converted PDF to {len(images)} images in {temp_folder}")
        return image_paths, temp_folder
    except Exception as e:
        logger.error(f"Error converting PDF to images: {e}")
        raise

def image_to_base64(image_path):
    """Convert image to base64 string."""
    try:
        with Image.open(image_path) as img:
            buffered = BytesIO()
            img.save(buffered, format="JPEG")
            return base64.b64encode(buffered.getvalue()).decode()
    except Exception as e:
        logger.error(f"Error converting image to base64: {e}")
        raise

def process_image_with_claude(client, image_base64, page_number, total_pages):
    """Process image using Claude Vision API with enhanced context awareness."""
    try:
        prompt = f"""You are processing page {page_number} of {total_pages} from a packing list or invoice document.
            This page contains a table with product information. Maintain consistent column interpretation across all pages.

            Important Rules:
            1. The table structure is FIXED across all pages - every row must have the same column structure
            2. Each row represents a product entry with specific details
            3. Headers may or may not be repeated on each page - ignore headers if present and focus on data rows
            4. Empty cells should be preserved to maintain table structure

            Extract ONLY the following fields from each row, maintaining exact column order:
            1. Commodity Name: The product description/name (required)
            2. Qty: The quantity value (default to 1 if not found)
            3. UOM: Unit of Measure (default to 'BOX' if not found)

            Return ONLY a JSON array of objects with these exact fields: 'Commodity Name', 'Qty', 'UOM'.
            Each object must have all three fields, even if using default values.
            Do not include any commentary, headers, or additional information.

            Example format:
            [
                {{"Commodity Name": "Product A", "Qty": 10, "UOM": "BOX"}},
                {{"Commodity Name": "Product B", "Qty": 1, "UOM": "BOX"}}
            ]"""

        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=8192,
            temperature=0,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": image_base64
                            }
                        }
                    ]
                }
            ]
        )
        
        # Extract JSON from response
        response_text = message.content[0].text
        results = json.loads(response_text)
        
        # Validate results structure
        for item in results:
            if not isinstance(item, dict) or not all(k in item for k in ['Commodity Name', 'Qty', 'UOM']):
                logger.warning(f"Invalid item structure on page {page_number}: {item}")
                # Fix the item structure if needed
                item.setdefault('Commodity Name', '')
                item.setdefault('Qty', 1)
                item.setdefault('UOM', 'BOX')
        
        return results
    except Exception as e:
        logger.error(f"Error processing image with Claude (page {page_number}): {e}")
        raise

def save_to_csv(data, source_file):
    """Save extracted data to CSV with timestamp in output directory."""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = os.path.splitext(os.path.basename(source_file))[0]
        output_file = os.path.join(OUTPUT_DIR, f"{base_name}_{timestamp}.csv")
        
        with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=['Commodity Name', 'Qty', 'UOM'])
            writer.writeheader()
            writer.writerows(data)
        
        logger.info(f"Successfully saved data to {output_file}")
        return output_file
    except Exception as e:
        logger.error(f"Error saving to CSV: {e}")
        raise

def process_pdf_document(pdf_path):
    """Main function to process PDF and extract table data."""
    try:
        # Ensure directories exist
        ensure_directories()
        
        # Initialize Anthropic client
        client = setup_anthropic_client()
        
        # Convert PDF to images
        image_paths, temp_folder = convert_pdf_to_images(pdf_path)
        total_pages = len(image_paths)
        
        try:
            # Process each image and collect results
            all_results = []
            for page_num, image_path in enumerate(image_paths, 1):
                # Convert image to base64
                image_base64 = image_to_base64(image_path)
                
                # Process with Claude
                results = process_image_with_claude(client, image_base64, page_num, total_pages)
                
                # Validate and log page results
                logger.info(f"Page {page_num}: Extracted {len(results)} items")
                all_results.extend(results)
            
            # Save results to CSV
            output_file = save_to_csv(all_results, pdf_path)
            return output_file
            
        finally:
            # Clean up temporary files
            cleanup_temp_files(temp_folder)
    
    except Exception as e:
        logger.error(f"Error processing PDF document: {e}")
        raise

if __name__ == "__main__":
    pdf_file = "cipl/sample7_Invoice+Packing List-100015.pdf"
    try:
        output_file = process_pdf_document(pdf_file)
        print(f"Processing complete. Results saved to: {output_file}")
    except Exception as e:
        print(f"Error processing document: {e}")
