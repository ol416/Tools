from PyPDF2 import PdfReader
from wand.image import Image
from wand.color import Color
from PIL import Image as PImage
import os

def convert_pdf_to_image(pdf_path):
    # Create a temporary directory to store image files
    temp_dir = "temp_images"
    os.makedirs(temp_dir, exist_ok=True)
    
    # Initialize a list to store image paths
    image_paths = []

    # Open the PDF file
    with open(pdf_path, "rb") as pdf_file:
        reader = PdfReader(pdf_file)
        for i in range(len(reader.pages)):
            # Convert each page to an image
            with Image(filename=f"{pdf_path}[{i}]", resolution=300) as img:
                img.background_color = Color("white")
                img.alpha_channel = 'remove'
                img.format = 'jpg'
                
                # Save the image to the temporary directory
                image_path = f"{temp_dir}/page_{i+1}.jpg"
                img.save(filename=image_path)
                image_paths.append(image_path)

    return image_paths

def merge_images_vertically(image_paths, output_path):
    images = [PImage.open(img_path) for img_path in image_paths]
    # Concatenate images vertically
    widths, heights = zip(*(i.size for i in images))
    max_width = max(widths)
    total_height = sum(heights)
    new_image = PImage.new('RGB', (max_width, total_height))
    y_offset = 0
    for img in images:
        new_image.paste(img, (0, y_offset))
        y_offset += img.height

    # Save the merged image
    new_image.save(output_path)
    
    # Remove temporary image files
    for img_path in image_paths:
        os.remove(img_path)

def process_pdf_files(input_dir="./pdf_files", output_dir="./output_images"):
    os.makedirs(output_dir, exist_ok=True)
    
    # Process each PDF file in the input directory
    for filename in os.listdir(input_dir):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(input_dir, filename)
            print(f"Processing PDF: {pdf_path}")

            # Convert PDF to images
            image_paths = convert_pdf_to_image(pdf_path)

            # Merge images vertically if the PDF has multiple pages
            if len(image_paths) > 1:
                output_image_path = os.path.join(output_dir, f"{os.path.splitext(filename)[0]}.jpg")
                merge_images_vertically(image_paths, output_image_path)
                print(f"Merged images saved to: {output_image_path}")
            else:
                print("Single page PDF, no merging required.")

# 执行处理
process_pdf_files()
