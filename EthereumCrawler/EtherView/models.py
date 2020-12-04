from django.db import models
from django import forms
from datetime import date
from django.urls import reverse
# Create your models here.
class Transaction(models.Model):
    sender = models.CharField(max_length=100)
    reciever = models.CharField(max_length=100)
    value = models.DecimalField(max_digits=30, decimal_places=18)
    internal = models.BooleanField(default=False)
    timestamp = models.BigIntegerField(default=0)
    transaction_log = models.ForeignKey('TransactionLog', on_delete=models.CASCADE,related_name='transactions')

    def __str__(self):
        return f'Sender: {self.sender}, Reciever: {self.reciever}, Value: {self.value}'


class TransactionLog(models.Model):
    address = models.CharField(max_length=50)
    start_block = models.BigIntegerField()
    end_block = models.BigIntegerField(null = True, blank = True)

    def __str__(self):
        return f'Address: {self.address}, Start Block: {self.start_block}, End Block: {self.end_block}'

    def get_absolute_url(self):
        return reverse('transaction-log-detail', args=[str(self.id)])


class ETHBalanceLog(models.Model):
    address = models.CharField(max_length=1000)
    date = models.DateField('Date format: %Y-%m-%d', default=date.today)
    balance = models.DecimalField(max_digits=30, decimal_places=18)

    def __str__(self):
        return f'Address: {self.address}, Date: {self.date}, Balance: {self.balance}'

    def get_absolute_url(self):
        return reverse('eth-balance-log-detail', args=[str(self.id)])

class TokenBalanceLog(models.Model):
    name = models.CharField(max_length=100)
    address = models.ForeignKey('Account', on_delete=models.CASCADE,related_name='tokens')
    date = models.DateField('Date format: %Y-%m-%d', default=date.today)
    balance = models.DecimalField(max_digits=30, decimal_places=18)

    def __str__(self):
        return f'Token name: {self.name}, Address: {self.address}, Date: {self.date}, Balance: {self.balance}'

    def get_absolute_url(self):
        return reverse('token-balance-log-detail', args=[str(self.id)])

class Account(models.Model):
    address = models.CharField('Account address',max_length=1000)
    date = models.DateField('Date format: %Y-%m-%d', default=date.today)
    contract_address = models.CharField('Smart contract address',max_length=1000, null=True, blank=True)

    def __str__(self):
        return f'{self.address}'

    def get_absolute_url(self):
        return reverse('account-detail', args=[str(self.id)])



