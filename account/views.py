from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from .models import User, Farm
from .serializers import UserCreateSerializer, UserRetrieveUpdateSerializer, FarmSerializer

class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer  # Use the create serializer
    permission_classes = [AllowAny]

class RetrieveUpdateDeleteUserView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserRetrieveUpdateSerializer  # Use the retrieve/update serializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

class FarmRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = FarmSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Farm.objects.get_queryset()

    def get_object(self):
        # get all user's farms and return the first one
        farms = self.get_queryset().filter(user=self.request.user)
        farm_id = self.kwargs.get("pk")
        return get_object_or_404(farms, id=farm_id)

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_deleted = True
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
