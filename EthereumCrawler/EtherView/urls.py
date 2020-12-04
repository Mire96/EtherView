"""EthereumCrawler URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from .views import AccountListView, AccountDetailView, historical_token_balance_check, token_balance_check, index, query_transactions, TransactionLogListView, TransactionLogDetailView, eth_balance_check, ETHBalanceLogDetailView, ETHBalanceLogListView

urlpatterns = [
    path('', index, name='index'),
    path('query_transactions/', query_transactions, name='query-transactions'),
    path('transaction_logs/', TransactionLogListView.as_view(), name='transaction-log-list'),
    path('transaction_logs/<int:pk>', TransactionLogDetailView.as_view(), name='transaction-log-detail'),

    path('eth_balance_check/', eth_balance_check, name= 'eth-balance-check'),
    path('eth_balance_check/<int:pk>', ETHBalanceLogDetailView.as_view(), name= 'eth-balance-log-detail'),
    path('eth_balance_check/list/', ETHBalanceLogListView.as_view(), name= 'eth-balance-log-list'),

    path('token_balance_check/', token_balance_check, name='token-balance-check'),
    path('historical_token_balance_check/', historical_token_balance_check, name='historical-token-balance-check'),
    path('accounts/', AccountListView.as_view(), name='account-list'),
    path('account/<int:pk>', AccountDetailView.as_view(), name= 'account-detail'),


]