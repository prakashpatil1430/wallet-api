from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid


class Customer(models.Model):
    customer_id = models.CharField(max_length=200)
    customer_xid = models.UUIDField(unique=True,
                                    editable=False,
                                    default=uuid.uuid4)

    def __str__(self):
        return f'{str(self.id)} -- {self.customer_xid}'


class Admins(AbstractUser):

    customer = models.ForeignKey(
        Customer,
        related_name="customer_user",
        on_delete=models.CASCADE,
        null=True, blank=True
    )

    class Meta:
        db_table = 'admins'


class WalletDetails(models.Model):
    """ Wallet Details """

    user = models.ForeignKey(Customer,
                             related_name="wallet_user",
                             on_delete=models.CASCADE,
                             null=True, blank=True
                             )
    owned_by = models.TextField(max_length=150, null=True, blank=True)
    amount = models.FloatField(default=0.0)
    enabled_at = models.DateTimeField(blank=True, null=True)
    disabled_at = models.DateTimeField(blank=True, null=True)
    wallet_status = models.BooleanField(default=False)

    def __str__(self):
        return str(self.amount)

    class Meta:
        db_table = 'wallet_details'


class WalletTransactions(models.Model):
    """ Track of Wallet Transactions """

    user = models.ForeignKey(
        Customer, related_name="wallet_transactions_user",
        on_delete=models.CASCADE,
        null=True, blank=True)
    wallet = models.ForeignKey(
        WalletDetails, related_name="wallet_details",
        on_delete=models.CASCADE,
        null=True, blank=True)
    reference_id = models.CharField(max_length=150, null=True, blank=True)
    withdrawn_by = models.TextField(max_length=150, null=True, blank=True)
    deposited_by = models.TextField(max_length=150, null=True, blank=True)
    amount = models.FloatField(default=0.0)
    deposited_at = models.DateTimeField(blank=True, null=True)
    withdrawn_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.reference_id

    class Meta:
        db_table = 'wallet_transactions'
