import requests
from django.conf import settings
from django.http import JsonResponse
from rest_framework.views import APIView
from oauthlib.oauth2 import WebApplicationClient
from rest_framework import permissions, status
from account.models import User
from django.shortcuts import redirect
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from .serializers import TokenSerializer
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

client = WebApplicationClient(settings.GOOGLE_CLIENT_ID)

class GoogleLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="Initiates the Google OAuth2 login process",
        responses={302: "Redirects to Google's OAuth2 login page"}
    )
    def get(self, request):
        # Generate the Google authorization URL
        authorization_endpoint = 'https://accounts.google.com/o/oauth2/auth'
        request_uri = client.prepare_request_uri(
            authorization_endpoint,
            redirect_uri=settings.GOOGLE_REDIRECT_URI,
            scope=["openid", "email", "profile"],
        )
        return JsonResponse({'url': request_uri})


class GoogleCallbackView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = TokenSerializer

    @swagger_auto_schema(
        operation_description="Handles the Google OAuth2 callback",
        responses={200: TokenSerializer}
    )
    def get(self, request):
        # Get the authorization code from the callback request
        code = request.GET.get('code')
        if not code:
            return JsonResponse({'error': 'Authorization code not provided'}, status=400)
        
        # Exchange the authorization code for an access token
        token_url = 'https://oauth2.googleapis.com/token'
        token_data = {
            'code': code,
            'redirect_uri': settings.GOOGLE_REDIRECT_URI,
            'client_id': settings.GOOGLE_CLIENT_ID,
            'client_secret': settings.GOOGLE_CLIENT_SECRET,
            'grant_type': 'authorization_code'
        }
        token_response = requests.post(token_url, data=token_data)
        if token_response.status_code != 200:
            return JsonResponse({'error': 'Failed to obtain access token'}, status=token_response.status_code)
        
        token_json = token_response.json()
        access_token = token_json.get('access_token')
        refresh_token = token_json.get('refresh_token')
        if not access_token:
            return JsonResponse({'error': 'Access token not found'}, status=400)
        
        # Get the user's info from Google
        userinfo_endpoint = 'https://www.googleapis.com/oauth2/v3/userinfo'
        userinfo_response = requests.get(userinfo_endpoint, headers={'Authorization': f'Bearer {access_token}'})
        if userinfo_response.status_code != 200:
            return JsonResponse({'error': 'Failed to fetch user info'}, status=userinfo_response.status_code)
        
        userinfo_json = userinfo_response.json()
        email = userinfo_json.get('email')
        given_name = userinfo_json.get('given_name')
        family_name = userinfo_json.get('family_name')
        picture_url = userinfo_json.get('picture')
        
        # Find or create the user
        user, created = User.objects.get_or_create(email=email)
        
        # Update user info
        user.first_name = given_name
        user.last_name = family_name
        
        if picture_url:
            # Download the picture and save it to the user's profile_picture field
            picture_response = requests.get(picture_url)
            if picture_response.status_code == 200:
                # Create the file path
                file_name = f"profile_pictures/{user.id}.jpg"
                # Save the picture to the file system
                default_storage.save(file_name, ContentFile(picture_response.content))
                user.profile_picture.name = file_name
        
        user.save()
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)
        
        serializer = TokenSerializer(data={
            'access_token': access_token,
            'refresh_token': refresh_token
        })
        
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)