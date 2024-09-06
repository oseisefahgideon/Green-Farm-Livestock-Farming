import requests
from django.conf import settings
from django.http import JsonResponse
from rest_framework.views import APIView
from oauthlib.oauth2 import WebApplicationClient
from rest_framework import permissions, status, serializers
from account.models import User
from django.shortcuts import redirect
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from .serializers import TokenSerializer, GoogleLoginSerializer
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.contrib.auth import update_session_auth_hash
from django.views.generic import TemplateView
from django.urls import reverse

client = WebApplicationClient(settings.GOOGLE_CLIENT_ID)

class GoogleLoginView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = GoogleLoginSerializer

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

        return Response({'url': request_uri}, status=status.HTTP_200_OK)

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
        
        return Response({
            'access': access_token,
            'refresh': refresh_token
        }, status=status.HTTP_200_OK)
    

class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

class PasswordChangeView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PasswordChangeSerializer

    @swagger_auto_schema(
        operation_description="Change password with old password",
        request_body=PasswordChangeSerializer,
        responses={200: "Password changed successfully"}
    )
    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if not user.check_password(serializer.validated_data['old_password']):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            update_session_auth_hash(request, user)  # Important for keeping the user logged in
            return Response({"detail": "Password changed successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

class PasswordResetView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = PasswordResetSerializer

    @swagger_auto_schema(
        operation_description="Send password reset email",
        request_body=PasswordResetSerializer,
        responses={200: "Password reset email sent successfully"}
    )
    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.filter(email=email).first()
            if user:
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                
                # Update this line
                reset_url = reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
                
                # If you need to include the full URL (including domain), do this:
                full_reset_url = request.build_absolute_uri(reset_url)
                
                mail_subject = 'Reset your password'
                message = render_to_string('password_reset_email.html', {
                    'user': user,
                    'reset_url': full_reset_url,  # Use full_reset_url here
                })
                email_message = EmailMessage(
                    mail_subject, message, settings.EMAIL_HOST_USER, [email]
                )
                email_message.content_subtype = 'html'
                email_message.send()
            return Response({"detail": "Password reset email sent successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class PasswordResetConfirmSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True)

class PasswordResetConfirmView(TemplateView, APIView):
    template_name = 'password_reset_confirm.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['uidb64'] = self.kwargs['uidb64']
        context['token'] = self.kwargs['token']
        return context

    def post(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user and default_token_generator.check_token(user, token):
            new_password = request.data.get('new_password')
            if new_password:
                user.set_password(new_password)
                user.save()
                return Response({"detail": "Password reset successfully."}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "New password is required"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "Invalid token or user ID"}, status=status.HTTP_400_BAD_REQUEST)
        