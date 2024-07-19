from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.urls import path, include
from .views import GoogleLoginView, GoogleCallbackView


urlpatterns = [
    path("get-token/", TokenObtainPairView.as_view(), name="get_token"),
    path("refresh-token/", TokenRefreshView.as_view(), name="refresh_token"),
    path('google/login/', GoogleLoginView.as_view(), name='google_login'),
    path('google/callback/', GoogleCallbackView.as_view(), name='google_callback'),
]