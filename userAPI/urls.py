from django.urls import path
from userAPI import views
from .views import UploadImageView
from .views import TestView, UserView, UserLoginView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from .views import LogoutView


urlpatterns = [
    path('test', TestView.as_view()),
    path('create-user/', UserView.as_view()),
    path('get-user/', UserLoginView.as_view()),
    path('login-user/', UserLoginView.as_view()),
    path('logout-user/', LogoutView.as_view()),
    path('start_ai', views.start_ai_model),
    path('upload/', UploadImageView.as_view(), name='image-upload'),
]

# localhost:8000/api/v1.0/user/test