from rest_framework import serializers
from .models import Livestock, FeedingRecord, HealthRecord
from account.models import Farm, User

class LivestockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Livestock
        exclude = ['is_deleted']
        read_only_fields = ['id', 'created_at', 'updated_at', 'farm', 'tag_number']
   


class FeedingRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedingRecord
        exclude = ['is_deleted']
        read_only_fields = ['id', 'created_at', 'updated_at', 'livestock', 'administered_by']


class HealthRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthRecord
        exclude = ['is_deleted']
        read_only_fields = ['id', 'created_at', 'updated_at', 'livestock', 'administered_by']