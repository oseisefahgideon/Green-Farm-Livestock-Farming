# from django.contrib.auth.models import User
from .models import User, Farm
from rest_framework import generics
from .serializers import UserSerializer, FarmSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status


class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

class RetrieveUpdateDeleteUserView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class FarmRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = FarmSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Farm.objects.get_queryset()

    def get_object(self):
        # get all users companies and return the first one
        companies = self.get_queryset().filter(user=self.request.user)
        company_id = self.kwargs.get("pk")
        return get_object_or_404(companies, id=company_id)

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_deleted = True
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)