import cv2
import numpy as np
import os
import imutils  # ,pyttsx3
from tensorflow.keras.models import load_model
from tkinter import *
from PIL import Image, ImageTk
from tkinter import ttk

import _tkinter
# engine = pyttsx3.init()
win = Tk()
win.geometry("1300x680+10+10")


image_path = "test.jpeg"

img = Image.open(image_path)
img = ImageTk.PhotoImage(img)
lm = Label(win, image=img)
lm.pack()

l = Label(win)
l.place(x=50, y=50)

lf = Label(win)
lf.place(x=1000, y=490)

lh = Label(win)
lh.place(x=1000, y=50)

lp = Label(win)
lp.place(x=1000, y=270)

os.environ['TF_FORCE_GPU_ALLOW_GROWTH'] = 'true'

net = cv2.dnn.readNet("yolov3-custom_7000.weights", "yolov3-custom.cfg")
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)

model = load_model('helmet_nonhelmet_cnn.h5')
print('model loaded!!!')

cap = cv2.VideoCapture('video1.mov')
COLORS = [(0, 255, 0), (0, 0, 255)]

layer_names = net.getLayerNames()
output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]


def helmet_or_nohelmet(helmet_roi):
    try:

        helmet_roi = cv2.resize(helmet_roi, (224, 224))
        helmet_roi = np.array(helmet_roi, dtype='float32')
        helmet_roi = helmet_roi.reshape(1, 224, 224, 3)
        helmet_roi = helmet_roi / 255.0
        return int(model.predict(helmet_roi)[0][0])
    except:
        pass


def img_covertor(img):
    b, g, r = cv2.split(img)
    img = cv2.merge((r, g, b))
    img = cv2.resize(img, (240, 160), interpolation=cv2.INTER_AREA)
    img = Image.fromarray(img)
    return img


def img_covertor_main(img):
    b, g, r = cv2.split(img)
    img = cv2.merge((r, g, b))
    img = cv2.resize(img, (224, 224), interpolation=cv2.INTER_AREA)
    img = Image.fromarray(img)
    return img


def loading():
    p = ttk.Progressbar(win, length=100)
    p.place(x=1000, y=450)
    p["value"] = 50


global p
p = 1


def box_finder(boxes, classIds, confidences, img):
    indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
    global p

    for i in range(len(boxes)):
        if i in indexes:
            x, y, w, h = boxes[i]  # coordinate for full motor or normal biker image box
            color = [int(c) for c in COLORS[classIds[i]]]
            # green --> bike
            # red --> number plate
            if classIds[i] == 0:  # no motor bike
                helmet_roi = img[max(0, y):max(0, y) + max(0, h) // 4, max(0, x):max(0, x) + max(0, w)]
            else:  # motor bike detected
                # adjust the full box coordinate to get the numberplate box image only
                x_h = x - 60
                y_h = y - 350
                w_h = w + 100
                h_h = h + 100
                # cv2.rectangle(img, (x, y), (x + w, y + h),(255,255,250), 7)

                if y_h > 0 and x_h > 0:

                    c = helmet_or_nohelmet(img[y_h:y_h + h_h, x_h:x_h + w_h])  # crop the head part from whole biker image box
                    ## lq = Label(win,width=200,text=['   helmet   ','   no-helmet   '][c])
                    ## lq.place(x=0,y=2)

                    # cv2.putText(img,['helmet','no-helmet'][c],(x,y-100),cv2.FONT_HERSHEY_SIMPLEX,2,(0,255,0),2)
                    if ['helmet', 'no-helmet'][c] == "no-helmet":
                        imgtk = ImageTk.PhotoImage(
                            image=img_covertor(img[y_h:y_h + h_h, x_h:x_h + w_h]))  # display head
                        lh.imgtk = imgtk
                        lh.configure(image=imgtk)

                        imgtk = ImageTk.PhotoImage(image=img_covertor(img[y:y + h, x:x + w]))  # display number plate
                        lp.imgtk = imgtk
                        lp.configure(image=imgtk)

                        imgtk = ImageTk.PhotoImage(image=img_covertor(img))  # display full image
                        lf.imgtk = imgtk
                        lf.configure(image=imgtk)

                        # engine.say("person detected without helmet the number plate send")
                        # engine.runAndWait()
                        # plate = Toplevel(win)

                        cv2.imwrite(str(p) + "plate.jpg", img[y:y + h, x:x + w])
                        cv2.imwrite(str(p) + "head.jpg", img[y_h:y_h + h_h, x_h:x_h + w_h])

                        p = p + 1

                    # cv2.rectangle(img, (x_h, y_h), (x_h + w_h, y_h + h_h),(255,255,250),1)


def main():
    ret, img = cap.read()
    img = imutils.resize(img, height=500)
    #img = cv2.imread('images/test2.png')
    height, width = img.shape[:2]

    blob = cv2.dnn.blobFromImage(img, 0.00392, (416, 416), (0, 0, 0), True, crop=False)

    net.setInput(blob)
    outs = net.forward(output_layers)

    confidences = []
    boxes = []
    classIds = []

    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.3:
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)

                w = int(detection[2] * width)
                h = int(detection[3] * height)
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)

                boxes.append([x, y, w, h])
                confidences.append(float(confidence))
                classIds.append(class_id)

    box_finder(boxes, classIds, confidences, img)

    imgtk = ImageTk.PhotoImage(image=img_covertor_main(img))
    l.imgtk = imgtk
    l.configure(image=imgtk)
    l.after(1, main)


main()
win.mainloop()