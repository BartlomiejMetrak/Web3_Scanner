import requests

# Separate function for CoinGecko API
def get_token_price_coingecko(token_address):
    """
    Get the current price of a token in USD using CoinGecko API.
    """
    url = 'https://api.coingecko.com/api/v3/simple/token_price/ethereum'
    params = {
        'contract_addresses': token_address,
        'vs_currencies': 'usd'
    }
    response = requests.get(url, params=params, verify=False)
    data = response.json()
    price = data.get(token_address.lower(), {}).get('usd', None)
    return price