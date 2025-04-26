# forimage.py

from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os, tempfile, base64, cv2
import torch, easyocr, re
from ultralytics import YOLO

# Load environment variables
YOLO_MODEL_PATH = os.getenv("YOLO_MODEL_PATH", "weights/best.pt")

# Initialize Flask app and CORS
app = Flask(__name__)
CORS(app)

# Load YOLO model and OCR reader once
detector = YOLO(YOLO_MODEL_PATH)
reader   = easyocr.Reader(['en'], gpu=torch.cuda.is_available())

# Class names matching the model's training labels
classNames = ["with helmet", "without helmet", "rider", "number plate"]

@app.route('/', methods=['GET'])
def health_check():
    return "Detector is running. POST images to /detect and videos to /process_video", 200

@app.route('/detect', methods=['POST'])
def detect_objects():
    if 'image' not in request.files:
        return jsonify({"error": "No image provided"}), 400
    image_file = request.files['image']
    filename   = image_file.filename

    # (Override logic omitted here—keep your override if needed)

    # Save to temp, read, then delete
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
        tmp.write(image_file.read())
        tmp_path = tmp.name
    img = cv2.imread(tmp_path)
    os.remove(tmp_path)
    if img is None:
        return jsonify({"error": "Invalid image file"}), 400

    # (Your detection & OCR code here…)
    # …

    # Return filename & plate_text
    return jsonify({
        "filename": filename,
        "number_plate_text": plate_text
    })

@app.route('/process_video', methods=['POST'])
def process_video():
    if 'video' not in request.files:
        return jsonify({"error": "No video provided"}), 400
    vf     = request.files['video']
    tmp_in = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False).name
    tmp_out= tempfile.NamedTemporaryFile(suffix='.mp4', delete=False).name
    vf.save(tmp_in)

    cap   = cv2.VideoCapture(tmp_in)
    fps   = cap.get(cv2.CAP_PROP_FPS) or 20.0
    w     = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h     = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc= cv2.VideoWriter_fourcc(*'mp4v')
    out   = cv2.VideoWriter(tmp_out, fourcc, fps, (w,h))

    while True:
        ret, frame = cap.read()
        if not ret: break
        results = detector(frame)
        for res in results:
            for box in res.boxes.data.tolist():
                x1,y1,x2,y2,_,cls = map(int, box)
                color = (0,255,0) if cls==0 else (0,0,255)
                cv2.rectangle(frame, (x1,y1),(x2,y2), color, 2)
        out.write(frame)

    cap.release()
    out.release()
    return send_file(tmp_out, mimetype='video/mp4')

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5003))
    app.run(host='0.0.0.0', port=port)
