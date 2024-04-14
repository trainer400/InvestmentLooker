from coinbase.rest import RESTClient
from json import dumps


def get_current_price(client: RESTClient, coin_name: str):
    data = client.get_product(product_id=coin_name)
    return float(data["price"])


def get_coin_availability(client: RESTClient, currency_name: str):
    data = client.get_accounts()

    for account in data["accounts"]:
        if account["currency"] == currency_name:
            return float(account["available_balance"]["value"])

    return 0
