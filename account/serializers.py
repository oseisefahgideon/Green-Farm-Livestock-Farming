from rest_framework import serializers
from .models import User, Farm

class FarmSerializer(serializers.ModelSerializer):
    class Meta:
        model = Farm
        fields = ('farm_name', 'location')

class UserSerializer(serializers.ModelSerializer):
    farm = FarmSerializer(required=False)

    class Meta:
        model = User
        fields = ("id", "email", "password", "first_name", "last_name", "profile_picture", "phone_number", 
                  "date_of_birth", "gender", "address", "city", "state_province", 
                  "country", "postal_code", "farm")
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        farm_data = validated_data.pop('farm', None)
        user = User.objects.create_user(**validated_data)
        if farm_data:
            Farm.objects.filter(user=user).update(**farm_data)
        return user

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