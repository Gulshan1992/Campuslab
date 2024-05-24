from rest_framework import serializers
from .models import *
from django.utils.crypto import get_random_string

class AccountSerializer(serializers.ModelSerializer):
    # password = serializers.CharField(write_only=True)

    class Meta:
        model = Account
        fields = ['email', 'name', 'accountID', 'website','app_secret_token']
     
    def create(self, validated_data):
        app_secret_token = get_random_string(length=50)
        user = Account.objects.create(
            name=validated_data['name'],
            email=validated_data['email'],
            accountID=validated_data['accountID'],
            website=validated_data['website'],
            app_secret_token=app_secret_token,            
        )

        # Include the app_secret_token in the serializer's data
        serialized_data = super().to_representation(user)
        serialized_data['app_secret_token'] = app_secret_token
        return serialized_data

class DestinationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Destinations
        fields = ['id','account_id','url', 'http_method', 'headers']
     
    def create(self, validated_data):
        user = Destinations.objects.create(
            # id=validated_data['id'],
            account_id=validated_data['account_id'],
            url=validated_data['url'],
            http_method=validated_data['http_method'],
            headers=validated_data['headers'],
                      
        )
        return user