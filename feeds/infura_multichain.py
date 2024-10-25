import requests
import warnings
import urllib3
from web3 import Web3
from decimal import Decimal

from feeds.coingecko import *
from feeds.dexscreener import *

# Suppress only the InsecureRequestWarning
warnings.filterwarnings("ignore", category=urllib3.exceptions.InsecureRequestWarning)


# ABI (Application Binary Interface)?
# An ABI in the context of Ethereum and EVM-compatible blockchains is a JSON array that describes 
# the interface of a smart contract. It specifies the functions and events that the contract exposes,
# along with their inputs and outputs.
ERC20_ABI = [
    {
        'constant': True,
        'inputs': [{'name': '_owner', 'type': 'address'}],
        'name': 'balanceOf',
        'outputs': [{'name': 'balance', 'type': 'uint256'}],
        'type': 'function'
    },
    {
        'constant': True,
        'inputs': [],
        'name': 'decimals',
        'outputs': [{'name': '', 'type': 'uint8'}],
        'type': 'function'
    },
    {
        'constant': True,
        'inputs': [],
        'name': 'name',
        'outputs': [{'name': '', 'type': 'string'}],
        'type': 'function'
    },
    {
        'constant': True,
        'inputs': [],
        'name': 'symbol',
        'outputs': [{'name': '', 'type': 'string'}],
        'type': 'function'
    },
    {
        'anonymous': False,
        'inputs': [
            {'indexed': True, 'name': 'from', 'type': 'address'},
            {'indexed': True, 'name': 'to', 'type': 'address'},
            {'indexed': False, 'name': 'value', 'type': 'uint256'}
        ],
        'name': 'Transfer',
        'type': 'event'
    }
]

# Infura project credentials (these should be secure in real-world applications)
INFURA_PROJECT_ID = 'eebd5c281f89448da9f1c530de78fc90'
INFURA_PROJECT_SECRET = 'pnRixPvgzddLWvEuh4gVjpPJjtozeC9VpLT0PszFMv3geL3PBaQ+uA'

# Dictionary of Infura URLs for supported chains
INFURA_URLS = {
    'ethereum': f"https://:{INFURA_PROJECT_SECRET}@mainnet.infura.io/v3/{INFURA_PROJECT_ID}",
    'polygon': f"https://:{INFURA_PROJECT_SECRET}@polygon-mainnet.infura.io/v3/{INFURA_PROJECT_ID}",
    'optimism': f"https://:{INFURA_PROJECT_SECRET}@optimism-mainnet.infura.io/v3/{INFURA_PROJECT_ID}",
    'arbitrum': f"https://:{INFURA_PROJECT_SECRET}@arbitrum-mainnet.infura.io/v3/{INFURA_PROJECT_ID}",
    'bsc': f"https://:{INFURA_PROJECT_SECRET}@bsc-mainnet.infura.io/v3/{INFURA_PROJECT_ID}",
    # Add more supported chains if needed
}

class Web3Infura:

    """
    Documentation: https://docs.infura.io/api/networks/ethereum/quickstart#python
    
    Best for:
    >   Fetching real-time data directly accessible from the blockchain without 
        requiring extensive historical indexing.
    >   Getting account balances and token balances for known tokens.
    >   Retrieving token metadata such as name, symbol, and decimals.
    >   Interacting with smart contracts and calling their methods.
    >   Subscribing to real-time events (with some limitations due to the nature of HTTP providers).

    Limitations:
    >   Not efficient for fetching historical data that requires scanning the entire 
        blockchain or large ranges of blocks.
    >   Cannot easily retrieve all tokens held by an address without prior knowledge of the tokens.
    >   Difficult to obtain a complete transaction history for an address solely through the Web3 API 
        without running a full node and indexing the data yourself.

    Can You Get Transactions Made by a Specific Address via Infura?

    > Normal Transactions: The Web3 API does not provide a direct method to retrieve all transactions 
        made by a specific address. This is because Ethereum nodes (and by extension, Infura) do not 
        index transactions by address. To retrieve all transactions involving an address, you would need 
        to scan all blocks and transactions, which is not feasible via the standard Web3 API.
    > Internal Transactions: Similarly, internal transactions (calls made from one contract to another) 
        are not stored as separate transactions on the blockchain. They are internal to 
        the execution of a transaction and are not accessible via the Web3 API in a way that allows for 
        querying by address.

    Why Can Etherscan Provide This Data?

    Blockchain Explorer APIs like Etherscan index the entire blockchain data, including all transactions 
    and internal calls, into a database. This allows them to provide APIs that can query transactions 
    by address efficiently.

    Etherscan's API offers endpoints like txlist, txlistinternal, and tokentx, 
    which you referenced in your code snippet. These endpoints are possible because Etherscan has 
    processed and indexed the blockchain data in ways that standard nodes do not.
    """

    def __init__(self, chain='ethereum'):
        """
        Initialize the Web3Infura class with the selected chain.
        Supported chains: 'ethereum', 'polygon', 'optimism', 'arbitrum'
        """
        if chain not in INFURA_URLS:
            raise ValueError(f"Unsupported chain: {chain}")
        
        infura_url = INFURA_URLS[chain]
        self.web3 = Web3(Web3.HTTPProvider(infura_url, {'verify': False}))

        if not self.web3.is_connected():
            raise Exception(f"Failed to connect to {chain} via Infura.")

    def get_token_transfer_events(self, token_address, from_block, to_block, argument_filters={}):
        """
        Get Transfer events by contract address and additionally filter by specific address.
        Block range need to be low enough to return max 10000 results within a block range.
        argument_filters={'from': wallet_address}
        argument_filters={'to': wallet_address}
        """
        token_contract = self.web3.eth.contract(address=token_address, abi=ERC20_ABI)
        events = token_contract.events.Transfer.get_logs(
            from_block=from_block,
            to_block=to_block,
            argument_filters=argument_filters,
        )
        return events

    def get_native_balance(self, wallet_address):
        """
        Get the native currency balance of a wallet address.
        """
        try:
            balance_wei = self.web3.eth.get_balance(wallet_address)
            balance = self.web3.from_wei(balance_wei, 'ether')
            return balance
        except Exception as e:
            print(f"Error fetching native balance for address {wallet_address}: {e}")
            return None

    def get_token_balance(self, token_address, wallet_address):
        """
        Get the token balance of a wallet for a specific token.
        """
        token_contract = self.web3.eth.contract(address=token_address, abi=ERC20_ABI)
        balance = token_contract.functions.balanceOf(wallet_address).call()
        decimals = self.get_token_decimals(token_contract)
        adjusted_balance = Decimal(balance) / (Decimal(10) ** decimals)
        return adjusted_balance

    def get_token_decimals(self, token_contract):
        """
        Get the decimals of a token.
        """
        decimals = token_contract.functions.decimals().call()
        return decimals

    def get_token_name(self, token_contract):
        """
        Get the name of a token.
        """
        try:
            name = token_contract.functions.name().call()
        except Exception:
            name = None
        return name

    def get_token_symbol(self, token_contract):
        """
        Get the symbol of a token.
        """
        try:
            symbol = token_contract.functions.symbol().call()
        except Exception:
            symbol = None
        return symbol

    def get_token_info(self, token_address):
        """
        Get the token name, symbol, and decimals.
        """
        token_contract = self.web3.eth.contract(address=token_address, abi=ERC20_ABI)
        name = self.get_token_name(token_contract)
        symbol = self.get_token_symbol(token_contract)
        decimals = self.get_token_decimals(token_contract)
        return {'name': name, 'symbol': symbol, 'decimals': decimals}


def get_checksum_address(address):
    """
    Convert an Ethereum address to checksum format.
    """
    return Web3.to_checksum_address(address)

