from rest_framework import serializers

class TokenSerializer(serializers.Serializer):
    access_token = serializers.CharField()
    refresh_token = serializers.CharField()

class GoogleLoginSerializer(serializers.Serializer):
    url = serializers.URLField()