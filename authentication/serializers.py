from rest_framework import serializers

class TokenSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()

class GoogleLoginSerializer(serializers.Serializer):
    url = serializers.URLField()