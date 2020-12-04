from django import forms
from .models import TransactionLog, ETHBalanceLog, TokenBalanceLog, Account


class TransactionLogCreationForm(forms.ModelForm):
    class Meta:
        model = TransactionLog
        fields = ['address', 'start_block']

class ETHBalanceLogCreationForm(forms.ModelForm):
    class Meta:
        model = ETHBalanceLog
        fields = ['address', 'date']

class AccountCreationForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['address']


class HistoricalAccountCreationForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['address', 'date', 'contract_address']