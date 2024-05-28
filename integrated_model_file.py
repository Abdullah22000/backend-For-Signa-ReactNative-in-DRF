import cv2
from cvzone.HandTrackingModule import HandDetector
from cvzone.ClassificationModule import Classifier
import numpy as np
import math

detector = HandDetector(maxHands=1)
classifier = Classifier("Model\keras_model.h5", "Model\labels.txt")

offset = 20
imgSize = 300

labels = ["A","B","C","D","E","F","G","I","L","ok","orange","PlayDead","Sit","Wait","Y","You"]

img = cv2.imread("backendSigna\myTest_image.jpg")
imgOutput = img.copy()
hands, img = detector.findHands(img)

def preprocess_image(img):
    """Preprocess image to improve model accuracy"""
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # Convert to grayscale
    img = cv2.GaussianBlur(img, (5, 5), 0)  # Apply Gaussian blur
    img = cv2.equalizeHist(img)  # Apply histogram equalization
    img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)  # Convert back to BGR
    return img

if hands:
    hand = hands[0]
    x, y, w, h = hand['bbox']

    imgWhite = np.ones((imgSize, imgSize, 3), np.uint8) * 255
    imgCrop = img[y - offset:y + h + offset, x - offset:x + w + offset]

    imgCrop = preprocess_image(imgCrop)
    imgCropShape = imgCrop.shape

    aspectRatio = h / w

    if aspectRatio > 1:
        k = imgSize / h
        wCal = math.ceil(k * w)
        imgResize = cv2.resize(imgCrop, (wCal, imgSize))
        imgResizeShape = imgResize.shape
        wGap = math.ceil((imgSize - wCal) / 2)
        imgWhite[:, wGap:wCal + wGap] = imgResize
    else:
        k = imgSize / w
        hCal = math.ceil(k * h)
        imgResize = cv2.resize(imgCrop, (imgSize, hCal))
        imgResizeShape = imgResize.shape
        hGap = math.ceil((imgSize - hCal) / 2)
        imgWhite[hGap:hCal + hGap, :] = imgResize

    prediction, index = classifier.getPrediction(imgWhite, draw=False)
    cv2.putText(imgOutput, labels[index], (x, y - 20), cv2.FONT_HERSHEY_COMPLEX, 2, (255, 0, 255), 2)
    print("Result is ", labels[index])

# Optional: save or display the output image
# cv2.imshow('Image', imgOutput)
# cv2.waitKey(0)
# cv2.imwrite('output_image.jpg', imgOutput)
