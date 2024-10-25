import requests
import time
import warnings
import urllib3
import threading
import pandas as pd

from feeds.utility import *

# Set your API key (this is an example for Etherscan)
ETHERSCAN_API_KEY = 'KR52G3163AU9696NCAZ74CGFKJZV7GIIG6'



# Suppress only the InsecureRequestWarning
warnings.filterwarnings("ignore", category=urllib3.exceptions.InsecureRequestWarning)


class EtherscanAPIError(Exception):
    """Custom exception for Etherscan API errors."""
    pass


class EtherscanClient:

    """
    Documentation: https://docs.etherscan.io/
    
    Blockchain Explorer APIs: More efficient (than Infura) for retrieving data that requires historical 
    context or aggregation over many blocks and transactions. They are better suited for getting 
    transaction histories, lists of tokens held by an address, and other indexed data.
    """


    def __init__(self, api_key):
        self.api_key = api_key
        self.last_request_time = None
        self.min_interval = 1.0 / 4.0  # Max 4 requests per second
        self.lock = threading.Lock()

        self.base_url = "https://api.etherscan.io/api"

    def _make_request(self, params):
        with self.lock:
            now = time.perf_counter()
            if self.last_request_time is not None:
                elapsed = now - self.last_request_time
                if elapsed < self.min_interval:
                    time.sleep(self.min_interval - elapsed)
            self.last_request_time = time.perf_counter()

        try:
            response = requests.get(self.base_url, params=params, verify=False)
            response.raise_for_status()
        except requests.exceptions.HTTPError as http_err:
            raise EtherscanAPIError(f"HTTP error occurred: {http_err}")
        except Exception as err:
            raise EtherscanAPIError(f"An error occurred: {err}")

        try:
            data = response.json()
        except ValueError as json_err:
            raise EtherscanAPIError(f"JSON decode error: {json_err}")

        if data.get('status') != '1' and data.get('message') != 'OK':
            # Note: For empty result sets, Etherscan returns status '0' and message 'No transactions found'
            if data.get('message') == 'No transactions found':
                data['result'] = []
            else:
                raise EtherscanAPIError(f"Etherscan API error: {data.get('message', 'Unknown error')}")
        return data['result']

    def get_block_number_by_timestamp(self, timestamp, closest="before"):
        """
        Convert a UNIX timestamp to an Ethereum block number.
        """
        params = {
            'module': 'block',
            'action': 'getblocknobytime',
            'timestamp': timestamp,
            'closest': closest,
            'apikey': self.api_key
        }
        return self._make_request(params)
    
    def _fetch_pagination_data(self, params):
        frame = []
        last_block = params['startblock']
        keep_fetching = True

        while keep_fetching:
            print(f"Fetching blockchain data from block {last_block + 1}...")
            params['startblock'] = last_block + 1  # Move to the next block
            data = self._make_request(params)

            if not data:
                keep_fetching = False
            else:
                frame.extend(data)
                last_block = int(data[-1]['blockNumber'])
                print(f"last_block: {last_block}, Num trans: {len(data)}")
                
                if len(data) < params['offset']:
                    keep_fetching = False

        # df.to_excel("Web3Bots\\sample_transactions.xlsx")
        return pd.DataFrame(frame)

    def get_token_transfers_by_address(self, address=None, contract_address=None, start_block=0, end_block=None):
            """
            Get all token transactions for a given contract and return as a DataFrame.
            """
            params = {
                'module': 'account',
                'action': 'tokentx',
                'startblock': start_block,
                'sort': 'asc',
                'apikey': self.api_key,
                'offset': 10000  # Adjust as needed
            }

            if contract_address:
                params['contractaddress'] = contract_address
            
            if address:
                params['address'] = address
            
            if end_block:
                params['endblock'] = end_block
            
            data = self._fetch_pagination_data(params)
            return data
    
    def get_normal_transactions_by_address(self, address, start_block:int=0, end_block:int=None):
        params = {
                'module': 'account',
                'action': 'txlist',
                'address': address,
                'startblock': start_block,
                'sort': 'asc',
                'apikey': self.api_key,
                'offset': 10000
            }

        if end_block:
            params['endblock'] = end_block
        
        data = self._fetch_pagination_data(params)
        return data

    def get_internal_transactions_by_address(self, address, start_block:int=0, end_block:int=None):
        params = {
                'module': 'account',
                'action': 'txlistinternal',
                'address': address,
                'startblock': start_block,
                'sort': 'asc',
                'apikey': self.api_key,
                'offset': 10000
            }

        if end_block:
            params['endblock'] = end_block
        
        data = self._fetch_pagination_data(params)
        return data

    def get_eth_balance(self, address):
        """
        Get the ETH balance for a given address.
        """
        params = {
            'module': 'account',
            'action': 'balance',
            'address': address,
            'tag': 'latest',
            'apikey': self.api_key
        }
        return self._make_request(params)
    
    def get_multiple_addresses_balance(self, addresses:list):
        """
        Get the ETH balance for a given addresses list.
        """
        addresses = ",".join(addresses)
        params = {
            'module': 'account',
            'action': 'balancemulti',
            'address': addresses,
            'tag': 'latest',
            'apikey': self.api_key
        }
        return self._make_request(params)

    def get_token_balance(self, address, contract_address):
        """
        Get the token balance for a given address and token contract.
        """
        params = {
            'module': 'account',
            'action': 'tokenbalance',
            'contractaddress': contract_address,
            'address': address,
            'tag': 'latest',
            'apikey': self.api_key
        }
        return self._make_request(params)
