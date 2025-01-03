import argparse
from PIL import Image
import imutils
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
from skimage.segmentation import clear_border
from imutils import contours


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
    return jsonify({"total_amount": total_amount, "sender_names": sender_names, "checks_data": checks_data})

def process_text(text):
    logging.info(f"Extracted text: {text}")
    check_data = {
        "name_address": extract_name_address(text),
        "pay_to_order_of": extract_pay_to_order_of(text),
        "typed_amounts": extract_amounts(text),
        "handwritten_amounts": extract_handwritten_amounts(text),
        "routing_number": extract_routing_number(text),
        "account_number": extract_account_number(text)
    }
    check_data["total_amount"] = sum(check_data["typed_amounts"]) + sum(check_data["handwritten_amounts"])
    logging.info(f"Processed check data: {check_data}")
    return check_data

def extract_routing_number(text):
    match = re.search(r'Routing Number:\s*(\d+)', text, re.IGNORECASE)
    if match:
        return match.group(1)
    return None

def extract_account_number(text):
    match = re.search(r'Account Number:\s*(\d+)', text, re.IGNORECASE)
    if match:
        return match.group(1)
    return None

def extract_name_address(text):
    lines = text.split('\n')
    name_address = []
    for line in lines:
        if re.search(r'\d{1,3}\s+\w+', line):  # Look for lines with addresses
            name_address.append(line.strip())
        elif re.search(r'[A-Za-z]+', line):  # Look for lines with names
            name_address.append(line.strip())
    # Join the lines with a space and clean up any extra spaces
    cleaned_name_address = ' '.join(name_address).replace('  ', ' ')
    # Further clean up the text by removing unwanted characters
    cleaned_name_address = re.sub(r'[^A-Za-z0-9\s,.-]', '', cleaned_name_address)
    return cleaned_name_address

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

def extract_digits_and_symbols(image, charCnts, minW=5, minH=15):
    charIter = charCnts.__iter__()
    rois = []
    locs = []
    while True:
        try:
            c = next(charIter)
            (cX, cY, cW, cH) = cv2.boundingRect(c)
            roi = None
            if cW >= minW and cH >= minH:
                roi = image[cY:cY + cH, cX:cX + cW]
                rois.append(roi)
                locs.append((cX, cY, cX + cW, cY + cH))
            else:
                parts = [c, next(charIter), next(charIter)]
                (sXA, sYA, sXB, sYB) = (np.inf, np.inf, -np.inf, -np.inf)
                for p in parts:
                    (pX, pY, pW, pH) = cv2.boundingRect(p)
                    sXA = min(sXA, pX)
                    sYA = min(sYA, pY)
                    sXB = max(sXB, pX + pW)
                    sYB = max(sYB, pY + pH)
                roi = image[sYA:sYB, sXA:sXB]
                rois.append(roi)
                locs.append((sXA, sYA, sXB, sYB))
        except StopIteration:
            break
    return (rois, locs)

def preprocess_image(image_path):
    if isinstance(image_path, str):
        image = cv2.imread(image_path)
    else:
        image = cv2.cvtColor(np.array(image_path), cv2.COLOR_RGB2BGR)
    
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    # Use a different thresholding method
    _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    kernel = np.ones((1, 1), np.uint8)
    img_dilated = cv2.dilate(thresh, kernel, iterations=1)
    img_eroded = cv2.erode(img_dilated, kernel, iterations=1)
    # Additional morphological operations
    img_eroded = cv2.morphologyEx(img_eroded, cv2.MORPH_CLOSE, kernel)
    return img_eroded

def extract_text(image):
    custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz$.,:/-'
    tesseract_text = pytesseract.image_to_string(image, config=custom_config)
    logging.info(f"Extracted OCR text: {tesseract_text}")
    return tesseract_text

# Configure Tesseract OCR path
pytesseract.pytesseract.tesseract_cmd = r'/opt/homebrew/bin/tesseract'

# if __name__ == '__main__':
#     app.run(debug=True)
if __name__ == "__main__":
    import sys
    if len(sys.argv) == 1:
        app.run(debug=True)
    else:
        ap = argparse.ArgumentParser()
        ap.add_argument("-i", "--image", required=True, help="path to input image")
        ap.add_argument("-r", "--reference", required=True, help="path to reference MICR E-13B font")
        args = vars(ap.parse_args())

        charNames = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "T", "U", "A", "D"]
        ref = cv2.imread(args["reference"])
        ref = cv2.cvtColor(ref, cv2.COLOR_BGR2GRAY)
        ref = imutils.resize(ref, width=400)
        ref = cv2.threshold(ref, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

        refCnts = cv2.findContours(ref.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        refCnts = imutils.grab_contours(refCnts)
        refCnts = contours.sort_contours(refCnts, method="left-to-right")[0]

        refROIs = extract_digits_and_symbols(ref, refCnts, minW=10, minH=20)[0]
        chars = {}
        for (name, roi) in zip(charNames, refROIs):
            roi = cv2.resize(roi, (36, 36))
            chars[name] = roi

        rectKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (17, 7))
        output = []
        image = cv2.imread(args["image"])
        (h, w,) = image.shape[:2]
        delta = int(h - (h * 0.2))
        bottom = image[delta:h, 0:w]

        gray = cv2.cvtColor(bottom, cv2.COLOR_BGR2GRAY)
        blackhat = cv2.morphologyEx(gray, cv2.MORPH_BLACKHAT, rectKernel)

        gradX = cv2.Sobel(blackhat, ddepth=cv2.CV_32F, dx=1, dy=0, ksize=-1)
        gradX = np.absolute(gradX)
        (minVal, maxVal) = (np.min(gradX), np.max(gradX))
        gradX = (255 * ((gradX - minVal) / (maxVal - minVal)))
        gradX = gradX.astype("uint8")

        gradX = cv2.morphologyEx(gradX, cv2.MORPH_CLOSE, rectKernel)
        thresh = cv2.threshold(gradX, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        thresh = clear_border(thresh)

        groupCnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        groupCnts = imutils.grab_contours(groupCnts)
        groupLocs = []
        for (i, c) in enumerate(groupCnts):
            (x, y, w, h) = cv2.boundingRect(c)
            if w > 50 and h > 15:
                groupLocs.append((x, y, w, h))
        groupLocs = sorted(groupLocs, key=lambda x: x[0])

        for (gX, gY, gW, gH) in groupLocs:
            groupOutput = []
            groupROI = gray[gY:gY + gH, gX:gX + gW]
            groupThresh = cv2.threshold(groupROI, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

            charCnts = cv2.findContours(groupThresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            charCnts = imutils.grab_contours(charCnts)
            charCnts = contours.sort_contours(charCnts, method="left-to-right")[0]

            (rois, locs) = extract_digits_and_symbols(groupThresh, charCnts)
            for roi in rois:
                scores = []
                for charName in charNames:
                    result = cv2.matchTemplate(roi, chars[charName], cv2.TM_CCOEFF)
                    (_, score, _, _) = cv2.minMaxLoc(result)
                    scores.append(score)
                groupOutput.append(charNames[np.argmax(scores)])
            output.append("".join(groupOutput))

        print("Check OCR: {}".format(" ".join(output)))