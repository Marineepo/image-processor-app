from PIL import Image
import pytesseract
import cv2
import re
from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload_images():
    images = request.files.getlist('images')
    total = 0.0
    os.makedirs('temp', exist_ok=True)
    for image in images:
        image_path = f"temp/{image.filename}"
        image.save(image_path)
        preprocessed_image = preprocess_image(image_path)
        text = pytesseract.image_to_string(preprocessed_image)
        amounts = extract_amounts(text)
        total += sum(amounts)
    return jsonify({"total_amount": total})

def sum_amounts(image_paths):
    total = 0.0
    for image_path in image_paths:
        preprocessed_image = preprocess_image(image_path)
        text = pytesseract.image_to_string(preprocessed_image)
        amounts = extract_amounts(text)
        total += sum(amounts)
    return total


def extract_amounts(text):
    # Look for amounts in formats like "123.45" or "$123.45"
    amounts = re.findall(r'\$\d+\.\d{2}|\d+\.\d{2}', text)
    return [float(amount.strip('$')) for amount in amounts]

# # Example
# text = "Transaction: $100.50\nCheck Amount: 200.00"
# print(extract_amounts(text)) # Output: [100.5, 200.0]

def preprocess_image(image_path):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    return thresh

# Configure Tesseract OCR path
# pytesseract.pytesseract.tesseract_cmd = r'/path/to/tesseract'
pytesseract.pytesseract.tesseract_cmd = r'/usr/local/bin/tesseract'

def extract_text(image_path):
    with Image.open(image_path) as image:
        text = pytesseract.image_to_string(image)
    return text

# # Test the function
# print(extract_text('example_check.jpg'))

if __name__ == '__main__':
    app.run(debug=True)