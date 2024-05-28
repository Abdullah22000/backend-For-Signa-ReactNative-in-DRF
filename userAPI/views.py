from django.http import HttpResponse
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import generics
from .models import UploadedImage
from .serializers import UploadedImageSerializer

from rest_framework.permissions import IsAuthenticated

import threading

from .serializers import UserSerializer


import cv2
from cvzone.HandTrackingModule import HandDetector
from cvzone.ClassificationModule import Classifier
import numpy as np
import math
import time

# cap = cv2.VideoCapture(0)
detector = HandDetector(maxHands=1)
classifier = Classifier("Model\keras_model.h5","Model\labels.txt") 

offset = 20
imgSize = 300

counter = 0

labels = ["A","B","C","D","E","F","G","I","L","ok","orange","PlayDead","Sit","Wait","Y","You"]


class TestView(APIView):
    def get(self, request, format=None):
        print("API Was Called")
        return Response("You Made It", status=200)

class UserView(APIView):
    def post(self, request, format=None):
        print("Creating a user")

        user_data = request.data
        print(request.data)

        user_serializer = UserSerializer(data=user_data)
        if user_serializer.is_valid():
            user_serializer.save()
            return Response({"user": user_serializer.data}, status=200)
        return Response({"msg": "Err"}, status=400)


class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)
    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    authentication_classes = [JWTAuthentication]
    
    def post(self, request, format=None):
        username = request.data.get('username')
        password = request.data.get('password')

        # Filter user by email or username
        user_obj = User.objects.filter(email=username).first() or User.objects.filter(username=username).first()

        if user_obj is not None:
            # Authenticate user
            user = authenticate(username=user_obj.username, password=password)

            if user is not None:
                if user.is_active:
                    refresh = RefreshToken.for_user(user)
                    access_token = str(refresh.access_token)
                    user_serializer = UserSerializer(user)
                    return Response({
                        'refresh': str(refresh),
                        'access': access_token,
                        'user': user_serializer.data
                    }, status=status.HTTP_200_OK)
                else:
                    return Response({"error": "User account is disabled."}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"error": "Invalid username or password"}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)


def start_ai():
    print("ai model setting up")
    import artifical

def start_ai_model(request):
    if request.method == 'GET':
        process_thread = threading.Thread(target=start_ai)
        process_thread.start()
        return HttpResponse("ai model started running")
    

class UploadImageView(generics.CreateAPIView):
    queryset = UploadedImage.objects.all()
    serializer_class = UploadedImageSerializer

    def post(self, request, *args, **kwargs):
        # data=request.data["image"]
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save()
            image_path = instance.image.path
            #modelpart_start
            # success, img = cap.read()
            # img = cv2.imread("backendSigna\myTest_image.jpg")
            img = cv2.imread(image_path)
            
            imgOutput = img.copy()
            hands, img = detector.findHands(img)

            #This code is for cropping image
            if hands:
                hand = hands[0]
                x,y,w,h = hand['bbox']

                imgWhite = np.ones((imgSize,imgSize,3),np.uint8)*255 #img size is 300 by 300 uint8 is bytes
                imgCrop = img[y - offset:y + h + offset, x - offset:x + w + offset]

                imgCropShape = imgCrop.shape

                aspectRatio = h/w

                if aspectRatio > 1 :
                    k = imgSize/h
                    wCal = math.ceil(k*w)
                    imgResize = cv2.resize(imgCrop,(wCal, imgSize))
                    imgResizeShape = imgResize.shape
                    wGap = math.ceil((imgSize-wCal)/2)
                    imgWhite[:, wGap:wCal+wGap] = imgResize #to make it in center
                    prediction, index = classifier.getPrediction(imgWhite, draw=False) ##
                    print(prediction.index) ##

                else:
                    k = imgSize/w
                    hCal = math.ceil(k*h)
                    imgResize = cv2.resize(imgCrop,(imgSize, hCal))
                    imgResizeShape = imgResize.shape
                    hGap = math.ceil((imgSize-hCal)/2)
                    imgWhite[hGap:hCal + hGap, :] = imgResize
                    prediction, index = classifier.getPrediction(imgWhite, draw=False) ##

                cv2.putText(imgOutput, labels[index], (x,y - 20), cv2.FONT_HERSHEY_COMPLEX, 2, (255, 0, 255),2) ##
                print("Result is ",labels[index])
            #model_part_end
            print("ye hy image: ", image_path)
        return Response({'id':labels[index]}, status=status.HTTP_201_CREATED)



