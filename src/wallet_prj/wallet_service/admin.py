from django.contrib import admin
from .models import Customer, Admins, WalletDetails, WalletTransactions
# Register your models here.


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('customer_id', 'customer_xid')


@admin.register(Admins)
class MainAdmin(admin.ModelAdmin):
    list_display = ('customer', 'username')


@admin.register(WalletDetails)
class WalletDetailsAdmin(admin.ModelAdmin):
    list_display = ('user', 'owned_by', 'amount', 'enabled_at',
                    'disabled_at', 'wallet_status')


@admin.register(WalletTransactions)
class WalletTransactionsAdmin(admin.ModelAdmin):
    list_display = ('user', 'wallet', 'reference_id', 'withdrawn_by',
                    'deposited_by', 'amount', 'deposited_at', 'withdrawn_at')
