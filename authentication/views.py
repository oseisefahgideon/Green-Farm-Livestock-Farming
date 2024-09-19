from django.conf import settings
from rest_framework.views import APIView
from rest_framework import permissions, status, serializers
from account.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from .serializers import TokenSerializer
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
from google.oauth2.credentials import Credentials
from rest_framework.permissions import AllowAny


class GoogleLoginView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        flow = Flow.from_client_secrets_file(
            settings.GOOGLE_CLIENT_SECRETS_FILE,
            scopes=['openid', 'https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/userinfo.profile']
        )
        flow.redirect_uri = settings.GOOGLE_REDIRECT_URI

        authorization_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )

        return Response({'url': authorization_url}, status=status.HTTP_200_OK)

class GoogleCallbackView(APIView):
    permission_classes = [AllowAny]
    serializers = TokenSerializer

    def post(self, request):
        code = request.data.get('code')
        if not code:
            return Response({'error': 'Authorization code not provided'}, status=status.HTTP_400_BAD_REQUEST)

        flow = Flow.from_client_secrets_file(
            settings.GOOGLE_CLIENT_SECRETS_FILE,
            scopes=['openid', 'https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/userinfo.profile'],
            redirect_uri=settings.GOOGLE_REDIRECT_URI
        )

        try:
            flow.fetch_token(code=code)
        except Exception as e:
            return Response({'error': 'Failed to fetch token'}, status=status.HTTP_400_BAD_REQUEST)

        credentials = flow.credentials

        user_info_service = build('oauth2', 'v2', credentials=credentials)
        user_info = user_info_service.userinfo().get().execute()

        email = user_info['email']
        first_name = user_info.get('given_name', '')
        last_name = user_info.get('family_name', '')
        picture = user_info.get('picture', '')

        user, created = User.objects.get_or_create(email=email)
        user.first_name = first_name
        user.last_name = last_name
        user.profile_picture = picture
        user.save()

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        return Response({
            'access_token': access_token,
            'refresh_token': str(refresh)
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
        