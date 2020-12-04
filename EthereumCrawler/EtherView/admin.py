from django.contrib import admin
from .models import Transaction, TransactionLog, ETHBalanceLog, TokenBalanceLog, Account

# Register your models here.
admin.site.register(Transaction)
admin.site.register(TransactionLog)
admin.site.register(ETHBalanceLog)
admin.site.register(TokenBalanceLog)
admin.site.register(Account)