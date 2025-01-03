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
import logging


# CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})
logging.basicConfig(level=logging.INFO)
app = Flask(__name__)
CORS(app)

@app.route('/upload_check', methods=['POST'])
def upload_check():
    logging.info("Received a POST request for check")
    images = request.files.getlist('images')
    logging.info(f"Number of images received: {len(images)}")
    checks_data = []
    os.makedirs('temp', exist_ok=True)
    for image in images:
        image_path = f"temp/{image.filename}"
        image.save(image_path)
        logging.info(f"Saved image to {image_path}")
        if image.filename.lower().endswith('.pdf'):
            pages = pdf2image.convert_from_path(image_path)
            for page in pages:
                preprocessed_image = preprocess_image(page)
                text = extract_text(preprocessed_image)
                check_data = process_text(text)
                checks_data.append(check_data)
        else:
            preprocessed_image = preprocess_image(image_path)
            text = extract_text(preprocessed_image)
            check_data = process_text(text)
            checks_data.append(check_data)
    
    total_amount = sum(check['total_amount'] for check in checks_data)
    sender_names = [check['name_address'] for check in checks_data if check['name_address']]
    return jsonify({"total_amount": total_amount, "sender_names": sender_names})

def process_text(text):
    logging.info(f"Extracted text: {text}")
    check_data = {
        "name_address": extract_name_address(text),
        "pay_to_order_of": extract_pay_to_order_of(text),
        "typed_amounts": extract_amounts(text),
        "handwritten_amounts": extract_handwritten_amounts(text)
    }
    check_data["total_amount"] = sum(check_data["typed_amounts"]) + sum(check_data["handwritten_amounts"])
    logging.info(f"Processed check data: {check_data}")
    return check_data

def extract_name_address(text):
    lines = text.split('\n')
    name_address = []
    for line in lines[:5]:
        if line.strip():
            name_address.append(line.strip())
    return ' '.join(name_address)

def extract_pay_to_order_of(text):
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
    amounts = re.findall(r'\$\d+\.\d{2}|\d+\.\d{2}', text)
    return [float(amount.strip('$')) for amount in amounts]

def extract_handwritten_amounts(text):
    handwritten_amounts = []
    matches = re.findall(r'([a-zA-Z\s]+)\s+(\d{1,2})/(\d{2})', text)
    for match in matches:
        words, numerator, denominator = match
        try:
            number = w2n.word_to_num(words.strip())
            fraction = float(numerator) / float(denominator)
            handwritten_amounts.append(number + fraction)
        except ValueError:
            logging.error(f"Failed to convert words to number: {words.strip()}")
            continue
    return handwritten_amounts

def preprocess_image(image_path):
    if isinstance(image_path, str):
        image = cv2.imread(image_path)
    else:
        image = cv2.cvtColor(np.array(image_path), cv2.COLOR_RGB2BGR)
    
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    kernel = np.ones((1, 1), np.uint8)
    img_dilated = cv2.dilate(thresh, kernel, iterations=1)
    img_eroded = cv2.erode(img_dilated, kernel, iterations=1)

    return img_eroded

def extract_text(image):
    custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz$.,:/-'
    tesseract_text = pytesseract.image_to_string(image, config=custom_config)
    return tesseract_text

# Configure Tesseract OCR path
pytesseract.pytesseract.tesseract_cmd = r'/opt/homebrew/bin/tesseract'

if __name__ == '__main__':
    app.run(debug=True)