from PIL import Image
import numpy as np
import pytesseract
import cv2
import re
from flask import Flask, request, jsonify
import os
from word2number import w2n
from flask_cors import CORS
import pdf2image



# CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})
app = Flask(__name__)
CORS(app)

@app.route('/upload_check', methods=['POST'])
def upload_check():
    print("Received a POST request for check")
    images = request.files.getlist('images')
    print(f"Number of images received: {len(images)}")
    total = 0.0
    sender_names = []
    os.makedirs('temp', exist_ok=True)
    for image in images:
        image_path = f"temp/{image.filename}"
        image.save(image_path)
        print(f"Saved image to {image_path}")
        if image.filename.lower().endswith('.pdf'):
            pages = pdf2image.convert_from_path(image_path)
            for page in pages:
                preprocessed_image = preprocess_image(page)
                text = extract_text(preprocessed_image)
                process_text(text, sender_names, total)
        else:
            preprocessed_image = preprocess_image(image_path)
            text = extract_text(preprocessed_image)
            process_text(text, sender_names, total)
    return jsonify({"total_amount": total, "sender_names": sender_names})

def process_text(text, sender_names, total):
    print(f"Extracted text: {text}")
    name_address = extract_name_address(text)
    pay_to_order_of = extract_pay_to_order_of(text)
    amounts = extract_amounts(text)
    handwritten_amounts = extract_handwritten_amounts(text)
    print(f"Extracted name and address: {name_address}")
    print(f"Extracted 'PAY TO THE ORDER OF': {pay_to_order_of}")
    print(f"Extracted typed amounts: {amounts}")
    print(f"Extracted handwritten amounts: {handwritten_amounts}")
    total += sum(amounts) + sum(handwritten_amounts)
    if name_address:
        sender_names.append(name_address)
    if pay_to_order_of:
        sender_names.append(pay_to_order_of)

def extract_name_address(text):
    # Extract name and address from the top left of the check
    lines = text.split('\n')
    name_address = []
    for line in lines[:5]:  # Assuming the name and address are within the first 5 lines
        if line.strip():
            name_address.append(line.strip())
    return ' '.join(name_address)

def extract_pay_to_order_of(text):
    # Extract "PAY TO THE ORDER OF" and the following name
    match = re.search(r'PAY TO THE ORDER OF\s+([A-Za-z\s]+)', text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None

@app.route('/upload_invoice', methods=['POST'])
def upload_invoice():
    print("Received a POST request for invoice")
    images = request.files.getlist('images')
    print(f"Number of images received: {len(images)}")
    invoice_data = []
    os.makedirs('temp', exist_ok=True)
    for image in images:
        image_path = f"temp/{image.filename}"
        image.save(image_path)
        print(f"Saved image to {image_path}")
        preprocessed_image = preprocess_image(image_path)
        text = extract_text(preprocessed_image)
        print(f"Extracted text: {text}")
        invoice_info = extract_invoice_info(text)
        invoice_data.append(invoice_info)
    return jsonify({"invoice_data": invoice_data})

def extract_invoice_info(text):
    # Extract relevant information from the invoice text
    invoice_info = {}
    invoice_info['invoice_number'] = extract_invoice_number(text)
    invoice_info['invoice_date'] = extract_invoice_date(text)
    invoice_info['total_amount'] = extract_invoice_total_amount(text)
    return invoice_info

def extract_invoice_number(text):
    # Extract invoice number using a regex pattern
    match = re.search(r'Invoice Number:\s*(\S+)', text)
    if match:
        return match.group(1)
    return None

def extract_invoice_date(text):
    # Extract invoice date using a regex pattern
    match = re.search(r'Invoice Date:\s*(\S+)', text)
    if match:
        return match.group(1)
    return None

def extract_invoice_total_amount(text):
    # Extract total amount using a regex pattern
    match = re.search(r'Total Amount:\s*\$?(\d+\.\d{2})', text)
    if match:
        return float(match.group(1))
    return 0.0

def extract_amounts(text):
    # Look for amounts in formats like "123.45" or "$123.45"
    amounts = re.findall(r'\$\d+\.\d{2}|\d+\.\d{2}', text)
    return [float(amount.strip('$')) for amount in amounts]

def extract_handwritten_amounts(text):
    # Look for handwritten amounts in formats like "one hundred and ten 23/100"
    handwritten_amounts = []
    matches = re.findall(r'([a-zA-Z\s]+)\s+(\d{1,2})/(\d{2})', text)
    for match in matches:
        words, numerator, denominator = match
        try:
            number = w2n.word_to_num(words.strip())
            fraction = float(numerator) / float(denominator)
            handwritten_amounts.append(number + fraction)
        except ValueError:
            print(f"Failed to convert words to number: {words.strip()}")
            continue
    return handwritten_amounts

def extract_sender_name(text):
    # Look for common patterns for sender names
    # This is a simple heuristic and may need to be adjusted based on actual check formats
    match = re.search(r'(?i)(pay to the order of|pay to|payable to)\s+([A-Za-z\s]+)', text)
    if match:
        return match.group(2).strip()
    return None

def preprocess_image(image_path):
    if isinstance(image_path, str):
        image = cv2.imread(image_path)
    else:
        image = cv2.cvtColor(np.array(image_path), cv2.COLOR_RGB2BGR)
    
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply contrast adjustment
    gray = cv2.equalizeHist(gray)
    
    # Apply adaptive thresholding
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    
    # Additional preprocessing steps
    kernel = np.ones((1, 1), np.uint8)
    img_dilated = cv2.dilate(thresh, kernel, iterations=1)
    img_eroded = cv2.erode(img_dilated, kernel, iterations=1)

    return img_eroded

def extract_text(image):
    # Use Tesseract OCR with custom configuration
    custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz$.,:/-'
    tesseract_text = pytesseract.image_to_string(image, config=custom_config)
    return tesseract_text

# Configure Tesseract OCR path
pytesseract.pytesseract.tesseract_cmd = r'/opt/homebrew/bin/tesseract'

if __name__ == '__main__':
    app.run(debug=True)