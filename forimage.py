# forimage.py
from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request, jsonify
from flask_cors import CORS
import os, tempfile, base64, cv2, math
import torch
import easyocr
from ultralytics import YOLO

# Load environment variables
YOLO_MODEL_PATH = os.getenv("YOLO_MODEL_PATH", "weights/best.pt")

# Initialize Flask app and CORS
app = Flask(__name__)
CORS(app)

# Load YOLO model and OCR reader once
detector = YOLO(YOLO_MODEL_PATH)
reader = easyocr.Reader(['en'], gpu=torch.cuda.is_available())

# Class names matching the model's training labels
classNames = ["with helmet", "without helmet", "rider", "number plate"]

@app.route('/', methods=['GET'])
def health_check():
    return "Detector is running. POST images to /detect", 200

@app.route('/detect', methods=['POST'])
def detect_objects():
    # Ensure an image file was sent
    if 'image' not in request.files:
        return jsonify({"error": "No image provided"}), 400
    image_file = request.files['image']

    # Save uploaded image to a temp file
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
        tmp.write(image_file.read())
        tmp_path = tmp.name

    # Read image from disk
    img = cv2.imread(tmp_path)
    os.remove(tmp_path)
    if img is None:
        return jsonify({"error": "Invalid image file"}), 400

    # Perform object detection
    results = detector(img)

    # Tracking variables
    plate_text = ""
    helmet_violation = False

    # Parse detection results
    for res in results:
        for box in res.boxes.data.tolist():
            # box: [x1, y1, x2, y2, confidence, class]
            x1, y1, x2, y2, conf, cls = box
            x1, y1, x2, y2 = map(int, (x1, y1, x2, y2))
            cls = int(cls)
            label = classNames[cls]

            # Draw bounding box and label
            color = (0, 255, 0) if cls == 0 else ((0, 0, 255) if cls in [1, 3] else (255, 0, 0))
            cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
            cv2.putText(img, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

            # Violation detection logic
            if cls == 1:
                helmet_violation = True
            if cls == 3 and helmet_violation:
                # Crop number plate and extract text
                plate_crop = img[y1:y2, x1:x2]
                texts = reader.readtext(plate_crop)
                plate_text = "".join([t[1] for t in texts]).replace(" ", "")

    if not plate_text:
        plate_text = "No number plate detected"

    # Convert annotated image to base64
    _, buffer = cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, 90])
    img_b64 = base64.b64encode(buffer).decode('utf-8')

    return jsonify({
        "image": img_b64,
        "number_plate_text": plate_text
    })

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5003))
    app.run(host='0.0.0.0', port=port)
