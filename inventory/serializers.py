from rest_framework import serializers
from .models import Category, Product

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        exclude = ['is_deleted']
        read_only_fields = ['created_at', 'updated_at', 'created_by']

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        exclude = ['is_deleted']
        read_only_fields = ['created_at', 'updated_at', 'created_by']


class ProductUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        exclude = ['is_deleted']
        read_only_fields = ['created_at', 'updated_at', 'created_by', 'category']

    def update(self, instance, validated_data):
        category = instance.category
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        instance.category = category
        return instance