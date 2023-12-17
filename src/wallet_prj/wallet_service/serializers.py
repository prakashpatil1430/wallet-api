from rest_framework import serializers
from . models import Customer, WalletDetails


class UserLoginSerializer(serializers.ModelSerializer):

    class Meta:
        model = Customer
        fields = '__all__'


class WalletDetailsSerializers(serializers.ModelSerializer):

    class Meta:
        model = WalletDetails
        fields = '__all__'
