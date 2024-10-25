import requests

# Separate function for Dexscreener API
def get_token_price_dexscreener(token_address):
    """
    Get the current price of a token in USD using Dexscreener API.
    """
    url = f'https://api.dexscreener.io/latest/dex/tokens/{token_address}'
    response = requests.get(url, verify=False)
    if response.status_code != 200:
        print(f"Error fetching price from Dexscreener for token {token_address}")
        return None

    data = response.json()
    if 'pairs' not in data:
        print(f"No pairs found for token {token_address} on Dexscreener.")
        return None

    pairs = data['pairs']
    if not pairs:
        print(f"No trading pairs available for token {token_address}")
        return None

    # Select the pair with the highest liquidity
    selected_pair = max(pairs, key=lambda x: float(x.get('liquidity', {}).get('usd', 0)))
    price_usd = float(selected_pair.get('priceUsd', 0))
    if price_usd == 0:
        print(f"Price is zero for token {token_address} on Dexscreener.")
        return None

    return price_usd
