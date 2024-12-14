from PIL import Image

import pytesseract

# If you don't have tesseract executable in your PATH, include the following:
pytesseract.pytesseract.tesseract_cmd = r''
# Example tesseract_cmd = r'C:\Program Files (x86)\Tesseract-OCR\tesseract'


def parse_image(image_path, pytesseract_path, output_path) :
    pytesseract.pytesseract.tesseract_cmd = pytesseract_path
    text = pytesseract.image_to_string(Image.open(image_path))

    with open(output_path, 'w') as file:
        file.write(text)
