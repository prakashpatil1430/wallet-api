from django.db import transaction
from django.db import transaction  # Import the transaction module
from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.authtoken.models import Token
from .models import Customer, Admins, WalletDetails, WalletTransactions
from .serializers import UserLoginSerializer, WalletDetailsSerializers, WalletTransactionsSerializers
from rest_framework import status
from datetime import datetime as dt

from .common_functions import get_json_errors, generate_random_reference_id
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
            'amount': data['amount']
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
                    'amount',
                    'transaction_type'
            )

            balance = 0
            for transaction in transactions:
                if transaction['deposited_by'] and transaction['transaction_type'] == 'deposit':
                    balance += transaction['amount']
                else:
                    balance -= transaction['amount']
                wallet_details.amount = balance
                wallet_details.save()

            response['data']['wallet']['amount'] = wallet_details.amount
            return Response(response)
        else:
            response['status'] = 'fail'
            response['data'] = {'error': 'wallet disabled'}
            response['status_code'] = status.HTTP_404_NOT_FOUND
        return Response(response)
    
    def patch(self, request):
        res = {}

        post_data = WalletDetailsSerializers(data=request.data)
        if post_data.is_valid():
            find_user = Customer.objects.filter(id=request.user.customer_id).first()

            wallet_exists = WalletDetails.objects.filter(
                user_id=find_user.id, wallet_status=True
            ).exists()

            if wallet_exists:
                # Disable the wallet and update the details
                WalletDetails.objects.filter(user_id=find_user.id, wallet_status=True).update(
                    wallet_status=False,
                    disabled_at=dt.now()
                )

                # Retrieve updated wallet details
                wallet_details = WalletDetails.objects.filter(user_id=find_user.id).first()

                basic = {
                    'id': wallet_details.id,
                    'owned_by': wallet_details.owned_by,
                    'wallet_status': wallet_details.wallet_status,
                    'disabled_at': wallet_details.disabled_at,
                    'balance': 0,  
                }

                res['data'] = basic
                res["status_code"] = 1
                return Response(res, status=status.HTTP_200_OK)
            else:
                res['error_message'] = 'Wallet not found or already disabled'
        else:
            res['error_message'] = post_data.errors
            res["status_code"] = 0
        return Response(res, status=status.HTTP_400_BAD_REQUEST)


class WalletDeposits(GenericAPIView):
    serializer_class = WalletTransactionsSerializers

    def post(self, request):
        response = {'status': '', 'data': {}}

        postData = WalletTransactionsSerializers(data=request.data)
        if postData.is_valid():
            customer_id = request.user.customer_id

            find_customer = Customer.objects.filter(
                pk=customer_id
            ).first()

            check_wallet_exists = WalletDetails.objects.filter(
                owned_by=find_customer.customer_id
            ).first()

            if check_wallet_exists:
                reference_ids = generate_random_reference_id()

                wallet_exists = WalletDetails.objects.filter(
                    user_id=find_customer.id,
                    wallet_status=True
                ).first()

                if wallet_exists:
                    wallet_transaction = WalletTransactions.objects.create(
                        user_id=find_customer.id,
                        wallet_id=wallet_exists.id,
                        reference_id=reference_ids,
                        amount=postData.validated_data['amount'],
                        deposited_at=dt.now(),
                        deposited_by=find_customer.customer_id
                    )

                    serializer = WalletTransactionsSerializers(
                        wallet_transaction)
                    response['status'] = 'success'
                    response['data'] = serializer.data
                    response["status_code"] = status.HTTP_200_OK
                    return Response(response)
                else:
                    response['error_message'] = 'Please enable your wallet to check balance amount!'
                    response["status_code"] = status.HTTP_400_BAD_REQUEST
                    return Response(response)
            else:
                response['error_message'] = 'Wallet does not exist'
                response["status_code"] = status.HTTP_400_BAD_REQUEST
                return Response(response)
        else:
            response['error_message'] = postData.errors
            response["status_code"] = status.HTTP_400_BAD_REQUEST
            return Response(response)


class WalletTransactionView(GenericAPIView):
    serializer_class = WalletTransactionsSerializers

    def get(self, request):
        response = {'status': '', 'data': {}}

        find_user = Customer.objects.filter(
            id=request.user.customer_id).first()

        if find_user:
            wallet_details = WalletDetails.objects.filter(
                user=find_user.id, wallet_status=True).first()

            if wallet_details:
                wallet_transactions = WalletTransactions.objects.filter(
                    user=find_user, wallet=wallet_details
                )

                all_trans = []
                for wallet_trans in wallet_transactions:
                    transaction_data = {
                        'id': wallet_trans.id,
                        'status': 'success',
                        'transaction_at': '',
                        'type': wallet_trans.transaction_type,
                        'amount': wallet_trans.amount,
                        'reference_id': wallet_trans.reference_id
                    }
                    transaction_data['transaction_at'] = (
                        wallet_trans.deposited_at
                        if wallet_trans.transaction_type == 'deposit'
                        else wallet_trans.withdrawn_at
                    )
                    all_trans.append(transaction_data)

                response['status'] = 'success'
                response['data']['transaction'] = all_trans

            else:
                response['status'] = 'fail'
                response['data'] = 'Wallet not found or disabled'
        else:
            response['status'] = 'fail'
            response['data'] = 'User not found'

        return Response(response)


# ... other imports


class WalletWithdrawals(GenericAPIView):
    serializer_class = WalletTransactionsSerializers

    def post(self, request):
        res = {'status_code': 0}

        post_data = WalletTransactionsSerializers(data=request.data)
        if post_data.is_valid():
            customer_id = request.user.customer_id
            transaction_type = post_data.validated_data.get(
                'transaction_type', '').lower()
            find_user = get_object_or_404(Customer, id=customer_id)
            print(find_user)
            wallet_details = WalletDetails.objects.filter(
                user=find_user.id).first()
    
            if wallet_details and wallet_details.wallet_status:
                if transaction_type == 'withdraw' and wallet_details.amount >= post_data.validated_data.get('amount'):
                    with transaction.atomic():
                        reference_id = generate_random_reference_id()
                        wallet_transaction = WalletTransactions.objects.create(
                            user=find_user,
                            wallet=wallet_details,
                            reference_id=reference_id,
                            withdrawn_at=timezone.now(),
                            withdrawn_by=find_user.customer_id,
                            transaction_type=transaction_type,
                            amount=post_data.validated_data.get('amount')
                        )

                        # Deduct the amount from the WalletDetails model
                        # wallet_details.amount -= post_data.validated_data.get(
                        #     'amount')
                        # wallet_details.save()

                        basic = {
                            'id': wallet_transaction.id,
                            'reference_id': wallet_transaction.reference_id,
                            'amount': wallet_transaction.amount,
                            'withdrawn_by': wallet_transaction.withdrawn_by,
                            'withdrawn_at': wallet_transaction.withdrawn_at,
                        }

                        res['data'] = basic
                        res['status_code'] = 1
                        return Response(res)
                else:
                    res['error_message'] = 'Insufficient balance for withdrawal.'
            else:
                res['error_message'] = 'Please enable your wallet to perform transactions.'
        else:
            res['error_message'] = post_data.errors

        return Response(res)
