from web3 import Web3
from operator import itemgetter
from datetime import datetime, date

import requests
import json #Parsing api calls
import calendar #Used for converting timestamps to dates and vice-versa
from decimal import *
from bs4 import BeautifulSoup as bs #Manipulating the html page
import cloudscraper #Used for bypassing CloudFlare
from config import api_key, infura_key





infura_url = infura_key
w3 = Web3(Web3.HTTPProvider(infura_url))
apiToken = api_key




#Helper functions for transfering date to timestamp and vice-versa #####################################################
def timestampToDate(ts):
    return datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d')

def dateToTimestamp(date):
    return calendar.timegm(datetime.strptime(date, '%Y-%m-%d').timetuple())
########################################################################################################################


def getTransactionsFromBlockByAddress(address, block_number = 0, end_block = 0):
    if end_block == 0:
        end_block = w3.eth.blockNumber
    if(end_block < block_number):
        raise ValueError('Block number is higher than existing blocks in the chain!')
    if not w3.isAddress(address):
        raise KeyError('Invalid address')

    t_message = ''
    it_message = ''
    transaction_list = []
    internal_transaction_list = []

    url = f'https://api.etherscan.io/api?module=account&action=txlist&address={address}&startblock={block_number}&endblock={end_block}&sort=asc&apikey={apiToken}'
    data = requests.get(url)
    transaction_dict = data.json()

    if transaction_dict['result']:
        for transaction in transaction_dict['result']:
            value = w3.fromWei(int(transaction['value']), 'ether')
            timestamp = int(transaction['timeStamp'])
            trans_dict = {'sender': transaction['from'], 'reciever': transaction['to'], 'value': value,
                          'timestamp': timestamp, 'internal': False}
            transaction_list.append(trans_dict)

        # This part just writes the transactions to a txt file, not needed for proper app execution
        with open('transactionData.txt', 'w') as f:
            json.dump(transaction_dict, f)

    else:
        t_message += 'No transactions found'
        # raise LookupError('No transactions found')

    url = f'https://api.etherscan.io/api?module=account&action=txlistinternal&address={address}&startblock={block_number}&endblock={end_block}&sort=asc&apikey={apiToken}'
    data = requests.get(url)
    internal_transaction_dict = data.json()

    if internal_transaction_dict['result']:
        for transaction in internal_transaction_dict['result']:
            value = w3.fromWei(int(transaction['value']), 'ether')
            timestamp = int(transaction['timeStamp'])
            trans_dict = {'sender': transaction['from'], 'reciever': transaction['to'], 'value': value,
                          'timestamp': timestamp, 'internal': True}
            internal_transaction_list.append(trans_dict)

        with open('internalTransactionData.txt', 'w') as f:
            json.dump(transaction_dict, f)
    else:
        it_message += 'No internal transactions found'
        #raise LookupError('No internal transactions found')

    result_dict = {}
    result_dict['transaction_list'] = transaction_list
    result_dict['internal_transaction_list'] = internal_transaction_list
    result_dict['end_block'] = end_block
    result_dict['t_message'] = t_message
    result_dict['it_message'] = it_message

    return result_dict

#Helper function used to correct the date input from the user, so it can be entered in the form for Etherscan
def correctDateFormating(dt):
    #When working with a string uncomment this
    #dt = datetime.strptime(dt, '%Y-%m-%d')
    return f'{dt.month}.{dt.day}.{dt.year}'




def bsGetBalanceAtTime(balance_date, address):
    if not w3.isAddress(address):
        raise KeyError('Invalid address!')

    #This conversion is needed while testing outside of django
    #balance_date = datetime.strptime(balance_date, '%Y-%m-%d')

    if balance_date>date.today():
        raise ValueError('Date is in the future!')
    dt = correctDateFormating(balance_date)
    scraper = cloudscraper.CloudScraper() #Bypassing cloudflare

    #Populating required parameters for form submission
    rp = scraper.get('https://etherscan.io/balancecheck-tool')
    sp = bs(rp.text, 'html.parser')
    event_target = sp.find(id="__EVENTTARGET").get('value')
    event_argument = sp.find(id="__EVENTARGUMENT").get('value')
    view_state = sp.find(id="__VIEWSTATE").get('value')
    view_state_gen = sp.find(id="__VIEWSTATEGENERATOR").get('value')
    event_validation = sp.find(id="__EVENTVALIDATION").get('value')
    params = {'__EVENTTARGET': event_target,
              '__EVENTARGUMENT': event_argument,
              '__VIEWSTATE': view_state,
              '__VIEWSTATEGENERATOR': view_state_gen,
              '__EVENTVALIDATION':event_validation,
              'ctl00$ContentPlaceHolder1$txtAddress': address,
              'date': dt,
              'ctl00$ContentPlaceHolder1$txtBlockNo': '',
              'ctl00$ContentPlaceHolder1$Button1':'Lookup'
              }
    #Scraping the response for Eth balance
    response = scraper.post('https://etherscan.io/balancecheck-tool', data = params)
    soup = bs(response.text, 'html.parser')

    #Testing html
    with open('test.html', 'w') as f:
        f.write(response.text)

    balance = soup.find("span", {"class":"text-size-1 text-break"}).text.split()
    #To save this in the database, we must remove the text, so we can convert the balance
    ether_balance = Decimal(balance[0].replace(',',''))
    return ether_balance



def bsGetAllTokens(account_address):
    if not w3.isAddress(account_address):
        raise KeyError('Invalid address!')
    url = f'https://etherscan.io/address/{account_address}'
    scraper = cloudscraper.CloudScraper()
    response = scraper.get(url)
    soup = bs(response.text, 'html.parser')
    if not soup.find(id="ContentPlaceHolder1_tokenbalance"):
        raise ValueError('No tokens found on this account!')

    token_list = soup.find("ul", {"class":"list list-unstyled mb-0"})
    tokens = token_list.findAll("span", {"class":"list-amount link-hover__item hash-tag hash-tag--md text-truncate"})
    result = []
    for token in tokens:
        token_obj=token.text.split(maxsplit = 1)
        token_obj[0] = Decimal(token_obj[0].replace(',', ''))
        result.append(token_obj)

    with open('token_list.txt', 'w') as f:
        s = ''
        for token in result:
            s += f'{token[0]} of {token[1]}\n'
        f.write(s)

    return result





def bsGetTokenBalanceAtTime(balance_date, account_address, contract_address):
    #Checking if account address is okay
    if not w3.isAddress(account_address):
        raise KeyError('Invalid account address!')

    # Calling the url for given address to check if it's valid
    url = f'https://api.etherscan.io/api?module=contract&action=getabi&address={contract_address}&apikey={apiToken}'
    response = requests.get(url).json()



    if response['status'] != "1":
        raise ConnectionError('Invalid contract!')

    ##Use this if statement and ddate conversion outside of django
    #balance_date = datetime.strptime(balance_date, '%Y-%m-%d')
    #if balance_date >  datetime.now():


    #Use this for django
    if balance_date>date.today():
        raise ValueError('Date is in the future!')

    dt = correctDateFormating(balance_date)
    scraper = cloudscraper.CloudScraper() #Bypassing cloudflare

    #Populating required parameters for form submission
    rp = scraper.get('https://etherscan.io/tokencheck-tool')
    sp = bs(rp.text, 'html.parser')
    event_target = sp.find(id="__EVENTTARGET").get('value')
    event_argument = sp.find(id="__EVENTARGUMENT").get('value')
    view_state = sp.find(id="__VIEWSTATE").get('value')
    view_state_gen = sp.find(id="__VIEWSTATEGENERATOR").get('value')
    event_validation = sp.find(id="__EVENTVALIDATION").get('value')
    params = {'__EVENTTARGET': event_target,
              '__EVENTARGUMENT': event_argument,
              '__VIEWSTATE': view_state,
              '__VIEWSTATEGENERATOR': view_state_gen,
              '__EVENTVALIDATION':event_validation,
              'ctl00$ContentPlaceHolder1$tokenbalance': 'tokenbalance',
              'ctl00$ContentPlaceHolder1$txtAccount': account_address,
              'ctl00$ContentPlaceHolder1$txtAddress': contract_address,
              'date': dt,
              'ctl00$ContentPlaceHolder1$txtBlockNo': '',
              'ctl00$ContentPlaceHolder1$Button1':'Lookup'
              }

    #Scraping the response for Eth balance
    response = scraper.post('https://etherscan.io/tokencheck-tool', data = params)
    soup = bs(response.text, 'html.parser')

    #Taking the token info from soup
    token = soup.findAll("span", {"class":"text-size-1"})[2].text.split()
    token_balance = Decimal(token[0].replace(',',''))
    token_name = token[1]

    result_dict = {}
    result_dict['token_name'] = token_name
    result_dict['token_balance'] = token_balance
    return result_dict


#Previous version of getting token balance for account with contract address
#Not used in the project
def getBalanceOfToken(account_address, contract_address):
    #Fetching contract abi
    url = f'https://api.etherscan.io/api?module=contract&action=getabi&address={contract_address}&apikey={apiToken}'
    response = requests.get(url).json()

    #Checking if contract and account address is okay
    if response['status'] != "1":
        raise KeyError('Invalid contract!')
    if not w3.isAddress(account_address):
        raise ValueError('Invalid address!')

    #Making the contract
    abi = response['result']
    contract = w3.eth.contract(address=contract_address, abi=abi)

    #Extracting balance and other info from the contract
    name = contract.functions.name().call()
    balance = w3.fromWei(contract.functions.balanceOf(w3.toChecksumAddress(account_address)).call(), 'ether')
    print(balance)
    #Preparing results
    result_dict = {}
    result_dict['token_name'] = name
    result_dict['token_balance'] = balance
    result_dict['account_address'] = account_address
    result_dict['contract_address'] = contract_address

    return result_dict


#This method is for calculating the balance of ether via incoming and outgoing transactions,
#but because the api is limited to 10,000 transactions it doesn't work for accounts with more transactions.
#Hence it's not used
def getValueOfEthAtTime(date, address):
    ts = dateToTimestamp(date)
    url = f'https://api.etherscan.io/api?module=block&action=getblocknobytime&timestamp={ts}&closest=before&apikey={apiToken}'
    rq_data = requests.get(url)
    transaction_dict = rq_data.json()
    end_block = int(transaction_dict['result'])
    block_url = f'https://api.etherscan.io/api?module=account&action=txlist&address={address}&startblock=0&endblock={end_block}&sort=asc&apikey={apiToken}'
    rq_data = requests.get(block_url).json()
    sums = Decimal(0)
    i_sum = Decimal(0)
    incoming = Decimal(0)
    outgoing = Decimal(0)
    transaction_fee = Decimal(0)

    for transaction in rq_data['result']:
        if int(transaction['nonce']) == 16:
            print('')
        if int(transaction['isError']) == 1:
            fee = w3.fromWei(Decimal(transaction['gasPrice']), 'ether') * Decimal(transaction['gasUsed'])
            transaction_fee += fee
            outgoing += fee
            sums -= fee
            continue
        if transaction['to'] == address.lower():
            eth_value = w3.fromWei(int(transaction['value']), 'ether')
            sums += eth_value
            incoming += eth_value
        if transaction['from'] == address.lower():
            eth_value = w3.fromWei(Decimal(transaction['value']), 'ether')
            fee = w3.fromWei(Decimal(transaction['gasPrice']), 'ether')*Decimal(transaction['gasUsed'])
            cost = eth_value + fee
            sums -= cost
            transaction_fee += fee
            outgoing += cost

    internal_url = f'https://api.etherscan.io/api?module=account&action=txlistinternal&address={address}&startblock=0&endblock={end_block}&sort=asc&apikey={apiToken}'
    rq_data = requests.get(internal_url).json()
    for transaction in rq_data['result']:
        if int(transaction['isError']) == 1:
            continue
        if transaction['to'] == address.lower():
            eth_value = w3.fromWei(int(transaction['value']), 'ether')
            i_sum += eth_value
            sums += eth_value
        if transaction['from'] == address.lower():
            eth_value = w3.fromWei(Decimal(transaction['value']), 'ether')
            transaction_fee = w3.fromWei(Decimal(transaction['gasPrice']), 'ether')*Decimal(transaction['gasUsed'])
            cost = eth_value + transaction_fee
            sums -= cost

    outgoing -= i_sum
    print("Calculated transaction fees: ")
    print(transaction_fee)
    print('My result in ether: ')
    print(sums)

    print("Incoming: ")
    print(incoming)
    print("Outgoing: ")
    print(outgoing)

#Archive node needed for this attempt
def infuraGetBalanceAtTime(date, address):
    ts = dateToTimestamp(date)
    url = f'https://api.etherscan.io/api?module=block&action=getblocknobytime&timestamp={ts}&closest=before&apikey={apiToken}'

    rq_data = requests.get(url)
    transaction_dict = rq_data.json()
    end_block = int(transaction_dict['result'])
    balance = w3.eth.getBalance(address, block_identifier = end_block)
    print(balance)

#First attempts at solving the problem
def getBalanceFromAccount(address):
    balance = w3.eth.getBalance(address)
    print('Wei: ')
    print(balance)
    print('Ether: ')
    print(w3.fromWei(balance, 'ether'))

def getBlocksFromToLast(block_number):
    latest_block = w3.eth.blockNumber
    i = block_number
    while(i <= latest_block):
        print(w3.eth.getBlock(i))
        i+=1







if __name__ == '__main__':
    #bs is short for BeautifulSoup, the package used for scraping info
    #bsGetBalanceAtTime('2020-12-1', '0x1fFa5Ef4B180E7B64E21D891A2abA5891fD85aa8')
    #bsGetAllTokens('0x1fFa5Ef4B180E7B64E21D891A2abA5891fD85aa8')
    #bsGetTokenBalanceAtTime(balance_date='2020-10-29',account_address= '0x2551d2357c8da54b7d330917e0e769d33f1f5b93', contract_address= '0xd26114cd6EE289AccF82350c8d8487fedB8A0C07')
    #getTransactionsFromBlockByAddress(address= '0x1fFa5Ef4B180E7B64E21D891A2abA5891fD85aa8', block_number=1654)

    #These functions were an attempt at solving the problem, but ultimately got replaced by the above functions
    #getBalanceFromAccount('0x1fFa5Ef4B180E7B64E21D891A2abA5891fD85aa8')
    #getValueOfEthAtTime('2020-10-29', '0x1fFa5Ef4B180E7B64E21D891A2abA5891fD85aa8')
    #infuraGetBalanceAtTime('2020-10-29', '0x1fFa5Ef4B180E7B64E21D891A2abA5891fD85aa8')
    #getBalanceOfToken(account_address= '0x2551d2357c8da54b7d330917e0e769d33f1f5b93', contract_address= '0xd26114cd6EE289AccF82350c8d8487fedB8A0C07')

    pass