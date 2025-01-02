# React TypeScript Check Extractor

This project is a React TypeScript application that allows users to upload check images via a drag-and-drop interface. The application processes the uploaded images to extract amounts and names using a Python backend.

## Features

- Drag and drop functionality for uploading check images.
- Submission of images to a backend service for processing.
- Display of extracted amounts and names.

## Project Structure
```
python3 -m venv venv
source venv/bin/activate

# Create requirements.txt and install dependencies
echo -e "Flask\npytesseract\nopencv-python\nPillow" > requirements.txt
pip install -r requirements.txt

# Run the Python file
python imageDataExtract.py
```

```
react-ts-check-extractor
├── public
│   ├── index.html        # Main HTML file
│   └── favicon.ico       # Application favicon
├── src
│   ├── components
│   │   ├── Dropzone.tsx  # Drag-and-drop component
│   │   └── ImageUploader.tsx # Component for uploading images
│   ├── App.tsx           # Main application component
│   ├── index.tsx         # Entry point of the application
│   └── types
│       └── index.ts      # TypeScript types and interfaces
├── package.json           # npm configuration
├── tsconfig.json          # TypeScript configuration
└── README.md              # Project documentation
```

## Setup Instructions

1. **Clone the repository:**
   ```
   git clone <repository-url>
   cd react-ts-check-extractor
   ```

2. **Install dependencies:**
   ```
   npm install
   ```

3. **Run the application:**
   ```
   npm start
   ```

4. **Access the application:**
   Open your browser and navigate to `http://localhost:3000`.

## Usage

- Drag and drop check images into the designated area.
- Click the submit button to send the images to the backend for processing.
- The extracted amounts and names will be displayed after processing.

## Backend Integration

Ensure that the Python backend is running and accessible for the image processing functionality to work correctly. Adjust the API endpoint in the `ImageUploader` component as necessary.

## License

This project is licensed under the MIT License.