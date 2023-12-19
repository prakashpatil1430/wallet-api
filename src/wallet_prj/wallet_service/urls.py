from django.urls import path
from . import views

urlpatterns = [
    path('v1/init/', views.UserLogin.as_view()),
    path('v1/wallet/', views.EnableWallet.as_view(), name='wallet_details'),
    path('v1/wallet/transactions/', views.WalletTransactionView.as_view(),
         name='wallet_deposit'),
    path('v1/wallet/deposits/', views.WalletDeposits.as_view(),
         name='wallet_deposit'),
    path('v1/wallet/withdraw/', views.WalletWithdrawals.as_view(),
         name='wallet_withdraw'),

]
