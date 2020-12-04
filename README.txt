
Hi, welcome to EtherView!
Project was codded in Python 3.9 using Pycharm community edition
This project uses the Web3 package for python and some API calls from Etherscan to gather andd store info about the Ethereum blockchain
The requirements.txt file holds packages and versions used.

Running the project:
-Download this project from git as a zip folder and extract it

-The Virtual environment should already be set up, so you just need to activate it.
To activate the environment, go open a command prompt and go into the Scripts folder (Location: EtherView-master/Scripts)
Then just type 'activate' and the name of the environment in brackets should appear next to the location in the command line.
In the same folder you can type 'deactivate' to deactivate the Virtual environment.

-Once you've activated the environment, change directories to EtherView-master/EthereumCrawler.
Then run the command: 'python manage.py runserver'
If successful, you should see in the command line that a development server was started at 'http://127.0.0.1:8000/'
You access the Django website through this link, which should take you to the index page. That's it!



Project functionalities:
The project is simple and has a few basic functionalities.

-Query transactions:
This link lets you input an Ethereum account address and a starting block number.
When you click search, it scans the blockchain starting from the block number and ending with the latest block,
and returns all transactions in which the account address was involved in (internal and external transactions)
It also saves all those transactions to the database for later viewing, which can take a few seconds.
It's not saving every transaction at a time, it puts them in a list and uses django's bulk create, to reduce calls to the database.

-Check ETH Balance:
This lets you input an address and a date (the date format is specified on the form).
After you click search, it searches for the account balance at the specified date.
This is also saved to the database for later viewing.


-Check Token Balance/Current:
This link lets you input an Ethereum account address.
After clicking search, the program will return token info (Excluding ETH) tied to the account.
Specifically, it returns the balance of other tokens on the account right now.
The address and tokens found are saved to the database for later viewing.


-Check Token Balance/Historical:
This link lets you input an Ethereum account address, a smart contract address for the token and date.
After clicking search the program returns historical data regarding a specific token.
Specifically, it returns the balance of this particular token for that account at the specified date.
All of this is saved to the database for later viewing.

-Previous queries:
This dropdown menu is used to access previous searches.

Transaction Logs lists all queries made through 'Query transactions',
after picking a specific transaction log it displays all transactions found on that query.

Historical ETH Balance lists all previous queries made by Check ETH Balance

Token balance lists all previous queries from Check Token Balance Current and Historical.


Important scripts:

-crawler.py:
This script is the logic of the project.
It has multiple functions that use either the Web3 package or Etherscan API.

Functions used in the project:
    bsGetBalanceAtTime - used for Check ETH Balance functionality
    bsGetAllTokens - used for Check Tokens Balance:Current
    bsGetTokenBalanceAtTime - used for Check Token Balance:Historical
    getTransactionsFromBlockByAddress - used for Query transactions

Functions not used in the project:
    getBalanceFromAccount - Uses web3.eth function to get current ETH balance from account
    getValueOfEthAtTime - This querries all transactions tied to the provided account and calculates the ETH balance at given date.
                        - Since the api limitations are 10000 transactions this function was replaced by bsGetBalanceAtTime
    infuraGetBalanceAtTime - Direct api call to get balance at specific time, but it requires an Archive node
    getBalanceOfToken - This function takes the smart contract address and account address and recreates the smart contract in python.
                      - Since it only works for current token balance, it was replacedd by bsGetAllTokens and bsGetTokkenBalanceAtTime


Important Django files:
(All files are in Ethereum Crawler/EthereumCrawler/EtherView)

-urls.py
This configures the paths on the website, which call view functions to render pages

-models.py
Defines the models which django then saves to the database as tables using it's ORM

-forms.py
Defines the fields for forms used in the project

-templates folder:
Hold all html files or webpages that are generated on the project


-views.py
This file defines the views or the logic behind the webpages.
In django urls call the views to execute the logic and views then render the webpages accordingly.

Important functions in views.py:
    query_transactions - handles the logic and renders the webpage for Query transactions
    eth_balance_check - handles the logic and renders the webpage for Check ETH balance
    historical_token_balance_check - handles the logic and renders the webpage for Check Token balance:Historical
    token_balance_check - handles the logic and renders the webpage for Check Token balance:Current

Classes DetailView and ListView:
    These views are just used to render the display of results.
    All of them call the database for retrieveing results,
    but in the comments I've written the logic for avoiding the database for Query transactions.
    As in, if we dont want to save all the transactions, but still want to see the results





