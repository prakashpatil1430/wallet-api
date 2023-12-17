from django.urls import path
from . import views

urlpatterns = [
    path('v1/init/', views.UserLogin.as_view()),
    path('v1/wallet/', views.EnableWallet.as_view(), name='wallet_details'),
]
