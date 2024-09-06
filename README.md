# TrafficVoilationMonitoring

## Traffic Violation Detection and E-Challan System

## Overview
This project is a web application that performs real-time object detection on video and image inputs to detect helmets and recognize license plate numbers on vehicles. The system automatically issues e-challans (fines) to violators by identifying traffic violations such as riding without a helmet. The following technologies and components have been used in the project: 

- **MERN Stack**: For building the web application. 
  - **MongoDB**: To store detected violations and user information.
  - **Express**: To handle backend APIs.
  - **React**: For the front-end user interface.
  - **Node.js**: Backend runtime environment.
- **YOLO (You Only Look Once)**: For object detection (helmets and license plates).
- **Twilio Messaging API**: To send e-challans to violators through SMS.

## How It Works
1. **Video Input**: An input video or image is uploaded to the web application.
2. **Object Detection**: YOLO is used to detect helmets and license plates from the video.
3. **Violation Identification**: If a violation (e.g., no helmet) is detected, the license plate number is extracted.
4. **E-Challan Generation**: The system stores the number plate of the violator.
5. **SMS Notification**: The violator receives an SMS with the fine details via Twilio.
