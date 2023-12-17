from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.authtoken.models import Token
from .models import Customer, Admins, WalletDetails, WalletTransactions
from .serializers import UserLoginSerializer, WalletDetailsSerializers
from rest_framework import status
from datetime import datetime as dt

from .common_functions import get_json_errors
from rest_framework import permissions


class UserLogin(GenericAPIView):
    serializer_class = UserLoginSerializer
    permission_classes = [permissions.AllowAny]

    @classmethod
    def post(cls, request):
        response = {}

        postData = UserLoginSerializer(data=request.data)
        if postData.is_valid():
            customer_id = postData.data['customer_id']

            customer = Customer.objects.filter(customer_id=customer_id).first()

            if not customer:
                customer = Customer.objects.create(
                    customer_id=customer_id)
                customer_xid = customer.customer_xid
                user_rec = Admins.objects.create(customer=customer,
                                                 username=customer_xid
                                                 )
            else:
                user_rec = Admins.objects.filter(
                    customer=customer,
                    username=customer.customer_xid
                ).first()

            token, _ = Token.objects.get_or_create(user=user_rec)

            if user_rec.id:
                response['customer_id'] = customer.customer_id
                response['customer_xid'] = customer.customer_xid
                response['data'] = {'token': token.key}
                response['status'] = 'success'
                return Response(response)
            else:
                response['errors'] = {'error': 'Customer not found'}
                response['status'] = 0
                return Response(response, status=404)
        else:
            response['errors'] = get_json_errors(postData.errors)
            response['status'] = 0
            return Response(response)


class EnableWallet(GenericAPIView):
    serializer_class = WalletDetailsSerializers

    def post(self, request):
        response_data = self.enable_wallet(
            request.data,
            request.user.customer_id
        )

        response_data['data'],
        response_data['status'],
        response_data['status_code']

        return Response(
            response_data
        )

    def enable_wallet(self, request_data, customer_id):
        response = {'status': '',
                    'data': {},
                    'status_code': status.HTTP_200_OK,
                    }

        serializer = self.serializer_class(data=request_data)
        if not serializer.is_valid():
            response['data'] = {'error_message': serializer.errors}
            response['status_code'] = status.HTTP_400_BAD_REQUEST
            return response

        customer = Customer.objects.filter(id=customer_id).first()
        wallet_exists = WalletDetails.objects.filter(
            user_id=customer.id).first()

        if not wallet_exists:
            WalletDetails.objects.create(
                user_id=customer.id,
                owned_by=customer.customer_id,
                wallet_status=True,
                enabled_at=dt.now()
            )
        else:
            wallet_status_check = WalletDetails.objects.filter(
                user_id=customer.id, wallet_status=True)
            if wallet_status_check.exists():
                response['data'] = {'error': 'Already enabled'}
                response['status'] = 'fail'
                response['status_code'] = status.HTTP_400_BAD_REQUEST
                print(response)
                return response

            WalletDetails.objects.filter(
                user_id=customer.id).update(wallet_status=True)

        wallet_details = WalletDetails.objects.filter(
            user_id=customer.id).first()
        data = WalletDetailsSerializers(wallet_details).data

        response['status'] = 'success'
        response['data']['wallet'] = {
            'id': data['id'],
            'owned_by': data['owned_by'],
            'status': 'enabled' if data['wallet_status'] else 'disabled',
            'enabled_at': data['enabled_at'],
            # Assuming 'amount' is the field for balance
            'balance': data['amount']
        }

        return response

    def get(self, request):
        response = {'status': 'success', 'data': {}}

        findcustomer = Customer.objects.filter(
            id=request.user.customer_id).first()

        wallet_details = WalletDetails.objects.filter(
            user=findcustomer.id, wallet_status=True).first()

        if wallet_details:
            wallet_info = WalletDetailsSerializers(wallet_details).data

            response['status'] = 'success'
            response['data']['wallet'] = wallet_info

            response['data']['wallet']['status'] = \
                'enabled' if wallet_info['wallet_status'] else 'disabled'

            # Fetch all transactions for the user
            transactions = WalletTransactions.objects.filter(
                user=findcustomer.id).values(
                    'deposited_by',
                    'withdrawn_by',
                    'amount'
            )

            balance = 0
            for transaction in transactions:
                if transaction['deposited_by']:
                    balance += transaction['amount']
                else:
                    balance -= transaction['amount']

            response['data']['wallet']['balance'] = balance
            return Response(response)
        else:
            response['status'] = 'fail'
            response['data'] = {'error': 'wallet disabled'}
            response['status_code'] = status.HTTP_404_NOT_FOUND
        return Response(response)

