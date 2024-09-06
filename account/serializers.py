from rest_framework import serializers
from .models import User, Farm

class FarmSerializer(serializers.ModelSerializer):
    class Meta:
        model = Farm
        read_only_fields = ("created", "updated", "user")
        exclude = ("is_deleted",)

# Serializer for creating users
class UserCreateSerializer(serializers.ModelSerializer):
    farm_id = serializers.SerializerMethodField()

    class Meta:
        model = User
        exclude = ["user_permissions", "groups", "is_superuser"]
        read_only_fields = ["last_login", "date_joined", "is_active", "is_staff"]
        extra_kwargs = {"password": {"write_only": True}}

    def get_farm_id(self, obj: User):
        farm = obj.farm_set.first()
        return farm.id if farm else None

    def create(self, validated_data):
        farm_data = validated_data.pop('farm', None)
        user = User.objects.create_user(**validated_data)
        if farm_data:
            Farm.objects.filter(user=user).update(**farm_data)
        return user

# Serializer for retrieving/updating users
class UserRetrieveUpdateSerializer(serializers.ModelSerializer):
    farm_id = serializers.SerializerMethodField()

    class Meta:
        model = User
        exclude = ["user_permissions", "groups", "is_superuser", "password"]  # Exclude password field
        read_only_fields = [
            "last_login",
            "date_joined",
            "is_active",
            "is_staff",
            "email"
        ]

    def get_farm_id(self, obj: User):
        farm = obj.farm_set.first()
        return farm.id if farm else None

    def update(self, instance, validated_data):
        farm_data = validated_data.pop('farm', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if farm_data:
            farm = instance.farm
            for attr, value in farm_data.items():
                setattr(farm, attr, value)
            farm.save()
        
        return instance
