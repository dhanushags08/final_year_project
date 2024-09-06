import base64
from flask import Flask, request, jsonify, send_file
import cv2
import math
import cvzone
import torch
import easyocr
from ultralytics import YOLO
import os
import io
import tempfile
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/detect": {"origins": "*"}})


@app.route('/detect', methods=['POST'])
def detect_objects():
    # Receive image file from the request
    image_file = request.files['image']

    # Save the received image to a temporary directory
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_image:
        temp_image_path = temp_image.name
        # Save the received image to the temporary file
        image_file.save(temp_image_path)

    # Load YOLO model with class names
    model = YOLO("best.pt")
    classNames = ["with helmet", "without helmet", "rider", "number plate"]

    # Load the input image
    img = cv2.imread(temp_image_path)

    # Perform object detection
    results = model(img)

    # Initialize number_plate_text outside the loop
    number_plate_text = ""

    # Flag to indicate if a rider without a helmet is detected
    rider_without_helmet_detected = False

    # Iterate over the results list
    for r in results:
        boxes = r.boxes
        xy = boxes.xyxy
        confidences = boxes.conf
        classes = boxes.cls
        new_boxes = torch.cat((xy, confidences.unsqueeze(1), classes.unsqueeze(1)), 1)

        # Extract bounding boxes, class IDs, and confidence scores
        for box in new_boxes:
            x1, y1, x2, y2 = int(box[0]), int(box[1]), int(box[2]), int(box[3])
            conf = math.ceil((box[4] * 100)) / 100
            cls = int(box[5])

            # Handle detections for riders without helmets
            if cls == 2 and conf > 0.5:  # Rider
                label = classNames[cls]
                rider_img = img[y1:y2, x1:x2]

                # Draw bounding box and label on the original image
                cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 0), 2)
                cv2.putText(img, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

                # Flag that a rider without a helmet is detected
                rider_without_helmet_detected = True

            # Handle detections for without helmet and number plate
            elif cls == 1 or cls == 3:  # Without helmet or number plate
                label = classNames[cls]

                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
                cv2.putText(img, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

                # Store the cropped number plate image when a rider without a helmet is detected
                if cls == 3 and rider_without_helmet_detected:
                    # Define the filename to save the cropped image
                    filename = "cropped_number_plate.jpg"

                    # Crop the region of interest (number plate)
                    number_plate_img = img[y1:y2, x1:x2]

                    # Save the cropped number plate image
                    cv2.imwrite(filename, number_plate_img)

                    # Use EasyOCR to extract the number plate text
                    reader = easyocr.Reader(['en'])
                    number_plate_text = reader.readtext(number_plate_img)

                    # Extract and print only the text from the number plate detection
                    number_plate_text = ''.join([text[1] for text in number_plate_text])
                    number_plate_text = number_plate_text.replace(" ", "")  # Remove white spaces
                    print("Number Plate:", number_plate_text)

    # Delete the temporary image file
    os.remove(temp_image_path)

    # Convert the image to base64 string
    _, buffer = cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, 90])
    img_base64 = base64.b64encode(buffer).decode('utf-8')

    # If number_plate_text is still empty, handle it
    if not number_plate_text:
        number_plate_text = "No number plate detected"

    response_data = {
        'image': img_base64,
        'number_plate_text': number_plate_text
    }

    return jsonify(response_data)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)
