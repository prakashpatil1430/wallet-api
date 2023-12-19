from rest_framework import serializers
from . models import Customer, WalletDetails, WalletTransactions


class UserLoginSerializer(serializers.ModelSerializer):

    class Meta:
        model = Customer
        fields = '__all__'


class WalletDetailsSerializers(serializers.ModelSerializer):

    class Meta:
        model = WalletDetails
        fields = '__all__'


class WalletTransactionsSerializers(serializers.ModelSerializer):

    @classmethod
    def validate(cls, data):
        errors = {}

        amount = data.get('amount')
        if not amount or amount == 0:
            errors['amount'] = 'Amount should be greater tha !'

        reference_id = data.get('reference_id')
        check_duplicate = WalletTransactions.objects.filter(
            reference_id=reference_id).exists()

        if check_duplicate:
            errors['reference_id'] = 'Duplicate Transaction Reference id. Please check'

        if errors:
            raise serializers.ValidationError(errors)

        return super(WalletTransactionsSerializers, cls).validate(cls, data)

    class Meta:
        model = WalletTransactions
        fields = '__all__'
