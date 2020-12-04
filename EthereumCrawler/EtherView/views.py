from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import TransactionLogCreationForm, ETHBalanceLogCreationForm, AccountCreationForm, HistoricalAccountCreationForm
from django.views.generic import ListView, DetailView
import crawler
from operator import itemgetter
from .models import TransactionLog, Transaction, ETHBalanceLog, TokenBalanceLog, Account

# Create your views here.

def index(request):
    context = {}
    return render(request,'index.html',context)

def query_transactions(request):
    if request.method == 'POST':
        form = TransactionLogCreationForm(request.POST)
        if form.is_valid():
            address = form.cleaned_data.get('address')
            block = form.cleaned_data.get('start_block')

            # Grabing the transactions from the API call, checking address and block number
            try:
                result_dict = crawler.getTransactionsFromBlockByAddress(address=address, block_number=block)

                internal_transaction_list = result_dict['internal_transaction_list']
                transaction_list = result_dict['transaction_list']
                all_transaction_list = internal_transaction_list + transaction_list
                all_transaction_list = sorted(all_transaction_list, key=itemgetter('timestamp'))
                end_block = result_dict['end_block']

            except ValueError:
                messages.warning(request, 'Block number higher than current number of blocks on the network!')
                return render(request, 'transaction-form.html', {'form': form})
            except KeyError:
                messages.warning(request, 'Invalid address!')
                return render(request, 'transaction-form.html', {'form': form})
            #except:
            #    messages.warning(request, 'No transactions found for the given address!')
            #    return render(request, 'transaction-form.html', {'form': form})

            #Saves the transaction log as an object for later viewing
            t_l = TransactionLog(address = address, start_block= block, end_block=end_block)
            t_l.save()


            #I started this project by wanting to save all transactions associated with a query in the database.
            #
            #Later i figured that a database representation might not be needed so i configured it both ways.
            #This part where we are saving all transactions in the database can be avoided.
            #If we want to avoid saving all transactions to the database, we can just comment out the next lines of code,
            #and then comment out the TransactionLogDetailView lines that call the crawler again, instead of calling the database.
            #Either way it works and no other code needs to be changed.
            #One exception is that, since transactions arent saved to the database, they dont have an id.


            #Instancing transaction objects to be saved in the database
            transaction_save_list = []
            transaction_object_list = []
            internal_transaction_object_list = []

            for transaction in all_transaction_list:
                transaction_object = Transaction(sender= transaction['sender'],reciever=transaction['reciever'],value = transaction['value'],timestamp= transaction['timestamp'],transaction_log= t_l, internal=transaction['internal'])
                if transaction['internal']:
                    internal_transaction_object_list.append(transaction_object)
                else:
                    transaction_object_list.append(transaction_object)
                transaction_save_list.append(transaction_object)

            #Bulk creating objects to reduce calls to the database
            Transaction.objects.bulk_create(transaction_save_list)

            if result_dict['it_message']!='' and result_dict['t_message']!='':
                messages.warning(request,f'No transactions found for the given address. Try another address or block number')
            else:
                messages.success(request, f'Query successful!')
                if result_dict['it_message'] != '':
                    messages.warning(request, f'No internal transactions found for the given address')
                if result_dict['t_message'] != '':
                    messages.warning(request, f'No normal transactions found for the given address')


            #Redirect to view the transactions just queried
            return redirect(t_l)
    else:
        form = TransactionLogCreationForm()
    return render(request, 'transaction-form.html', {'form': form})


class TransactionLogListView(ListView):
    model = TransactionLog
    template_name = 'transaction-log-list.html'

    def get_queryset(self):
        return TransactionLog.objects.all()


class TransactionLogDetailView(DetailView):
    model = TransactionLog
    template_name = 'transaction-log-detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        transaction_list = []
        internal_transaction_list = []
        for transaction in self.object.transactions.all():
            if transaction.internal:
                internal_transaction_list.append(transaction)
            else:
                transaction_list.append(transaction)

        #Splitting internal and normal transactions for better displaying on the view page
        context['transaction_list'] = transaction_list
        context['internal_transaction_list'] = internal_transaction_list


######## Or without calling the database and using the api instead: ####################################################
        #
        #address = self.object.address
        #start_block = self.object.start_block
        #end_block = self.object.end_block
        #internal_transaction_obj_list = []
        #transaction_obj_list = []
        #result_dict = crawler.getTransactionsFromBlockByAddress(address=address, block_number=start_block, end_block=end_block)
        #transaction_list = result_dict['transaction_list']
        #internal_transaction_list = result_dict['internal_transaction_list']
        #for transaction in transaction_list:
        #    transaction_object = Transaction(sender=transaction['sender'], reciever=transaction['reciever'],
        #                                     value=transaction['value'], timestamp=transaction['timestamp'],
        #                                     transaction_log=self.object, internal=transaction['internal'])
        #    transaction_obj_list.append(transaction_object)
        #for transaction in internal_transaction_list:
        #    transaction_object = Transaction(sender=transaction['sender'], reciever=transaction['reciever'],
        #                                     value=transaction['value'], timestamp=transaction['timestamp'],
        #                                      transaction_log=self.object, internal=transaction['internal'])
        #    internal_transaction_obj_list.append(transaction_object)
        #context['transaction_list'] = transaction_obj_list
        #context['internal_transaction_list'] = internal_transaction_obj_list

########################################################################################################################
        return context

# Bonus assignment: check historical ETH balance of an account##########################################################
def eth_balance_check(request):
    if request.method == 'POST':
        form = ETHBalanceLogCreationForm(request.POST)
        if form.is_valid():
            address = form.cleaned_data.get('address')
            balance_date = form.cleaned_data.get('date')
            #Checking if adddress is valid and date isn't a future date
            try:
                balance = crawler.bsGetBalanceAtTime(address=address, balance_date=balance_date)
            except KeyError:
                messages.warning(request, 'Invalid address!')
                return render(request, 'eth-balance-form.html', {'form': form})
            except ValueError:
                messages.warning(request, 'Date is in the future!')
                return render(request, 'eth-balance-form.html', {'form': form})
            eth_log = ETHBalanceLog(address=address, date=balance_date, balance=balance)
            eth_log.save()
            messages.success(request, f'Query successful!')

            return redirect(eth_log)
    else:
        form = ETHBalanceLogCreationForm()
    return render(request, 'eth-balance-form.html', {'form': form})


class ETHBalanceLogDetailView(DetailView):
    model = ETHBalanceLog
    template_name = 'eth-balance-log-detail.html'

class ETHBalanceLogListView(ListView):
    model = ETHBalanceLog
    template_name = 'eth-balance-log-list.html'

    def get_queryset(self):
        return ETHBalanceLog.objects.all()

#Bonus assignment: Check the ballance of different tokens for an account

def historical_token_balance_check(request):
    if request.method == 'POST':
        form = HistoricalAccountCreationForm(request.POST)
        if form.is_valid():
            contract_address = form.cleaned_data.get('contract_address')
            address = form.cleaned_data.get('address')
            date = form.cleaned_data.get('date')

            #Checking date, account address and contract address
            try:
                result = crawler.bsGetTokenBalanceAtTime(balance_date= date, account_address = address, contract_address = contract_address)
            except ConnectionError:
                messages.warning(request, 'Invalid contract address!')
                return render(request, 'token-balance-form.html', {'form': form})
            except KeyError:
                messages.warning(request, 'Invalid address!')
                return render(request, 'token-balance-form.html', {'form': form})
            except ValueError:
                messages.warning(request, 'Date is in the future!')
                return render(request, 'token-balance-form.html', {'form': form})


            account = Account(address=address)

            try:
                account = Account.objects.get(address=address)
            except:
                account.save()

            balance = result['token_balance']
            name = result['token_name']
            token_log = TokenBalanceLog(address=account, balance=balance, name=name, date=date)
            token_log.save()
            token_list = []
            token_list.append(token_log)

            messages.success(request, f'Query successful!')
            context = {'account':account,'token_list':token_list}
            return render(request, 'account-detail.html', context)
    else:
        form = HistoricalAccountCreationForm()
    return render(request, 'token-balance-form.html', {'form': form})



def token_balance_check(request):
    if request.method == 'POST':
        form = AccountCreationForm(request.POST)
        if form.is_valid():
            address = form.cleaned_data.get('address')
            token_save_list = []
            #Checking if address is valid
            try:
                result = crawler.bsGetAllTokens(account_address = address)
            except KeyError:
                messages.warning(request, 'Invalid address!')
                return render(request, 'token-balance-form.html', {'form': form})
            except ValueError:
                messages.warning(request, 'No other tokens found on this address!')
                return render(request, 'token-balance-form.html', {'form': form})


            account = Account(address=address)

            try:
                account = Account.objects.get(address=address)
            except:
                account.save()


            for token in result:
                balance = token[0]
                name = token[1]
                token_log = TokenBalanceLog(address=account, balance=balance, name=name)
                token_save_list.append(token_log)


            messages.success(request, f'Query successful!')
            TokenBalanceLog.objects.bulk_create(token_save_list)
            context = {'account': account, 'token_list': token_save_list}
            return render(request, 'account-detail.html', context)
            #return redirect(account)
    else:
        form = AccountCreationForm()
    return render(request, 'token-balance-form.html', {'form': form})


class AccountDetailView(DetailView):
    model = Account
    template_name = 'account-detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['token_list'] = self.object.tokens.all()
        return context

class AccountListView(ListView):
    model= Account
    template_name = 'account-list.html'
    def get_queryset(self):
        return Account.objects.all()



