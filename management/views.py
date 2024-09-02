from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, serializers
from .models import Livestock, FeedingRecord, HealthRecord
from .serializers import LivestockSerializer, FeedingRecordSerializer, HealthRecordSerializer

from account.models import Farm  

class LivestockListCreateView(generics.ListCreateAPIView):
    serializer_class = LivestockSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Return only livestock related to the current user's farm
        user_farm = Farm.objects.get(user=self.request.user)
        return Livestock.objects.filter(farm=user_farm)

    def perform_create(self, serializer):
        # Automatically set the farm field to the current user's farm
        user_farm = Farm.objects.get(user=self.request.user)
        serializer.save(farm=user_farm)

class LivestockRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = LivestockSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Return only livestock related to the current user's farm
        user_farm = Farm.objects.get(user=self.request.user)
        return Livestock.objects.filter(farm=user_farm)

class FeedingRecordListCreateView(generics.ListCreateAPIView):
    serializer_class = FeedingRecordSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        livestock_id = self.kwargs.get('livestock_id')
        if livestock_id:
            user_farm = Farm.objects.get(user=self.request.user)
            return FeedingRecord.objects.filter(livestock_id=livestock_id, livestock__farm=user_farm)
        return FeedingRecord.objects.none()

    def perform_create(self, serializer):
        livestock_id = self.kwargs.get('livestock_id')
        user_farm = Farm.objects.get(user=self.request.user)
        livestock = Livestock.objects.filter(id=livestock_id, farm=user_farm).first()
        if not livestock:
            raise serializers.ValidationError("Invalid livestock ID or livestock does not belong to your farm.")
        serializer.save(
            livestock=livestock,
            administered_by=self.request.user
        )

class FeedingRecordRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = FeedingRecordSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        livestock_id = self.kwargs.get('livestock_id')
        user_farm = Farm.objects.get(user=self.request.user)
        return FeedingRecord.objects.filter(livestock_id=livestock_id, livestock__farm=user_farm)
    
class HealthRecordListCreateView(generics.ListCreateAPIView):
    serializer_class = HealthRecordSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        livestock_id = self.kwargs.get('livestock_id')
        if livestock_id:
            user_farm = Farm.objects.get(user=self.request.user)
            return HealthRecord.objects.filter(livestock_id=livestock_id, livestock__farm=user_farm)
        return HealthRecord.objects.none()

    def perform_create(self, serializer):
        livestock_id = self.kwargs.get('livestock_id')
        user_farm = Farm.objects.get(user=self.request.user)
        livestock = Livestock.objects.filter(id=livestock_id, farm=user_farm).first()
        if not livestock:
            raise serializers.ValidationError("Invalid livestock ID or livestock does not belong to your farm.")
        serializer.save(
            livestock=livestock,
            administered_by=self.request.user
        )

class HealthRecordRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = HealthRecordSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        livestock_id = self.kwargs.get('livestock_id')
        user_farm = Farm.objects.get(user=self.request.user)
        return HealthRecord.objects.filter(livestock_id=livestock_id, livestock__farm=user_farm)