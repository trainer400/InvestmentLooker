from coinbase.rest import RESTClient
from json import dumps
import random


def get_current_price(client: RESTClient, coin_name: str):
    data = client.get_product(product_id=coin_name)
    return float(data["price"])


def get_coin_availability(client: RESTClient, currency_name: str):
    data = client.get_accounts()

    for account in data["accounts"]:
        if account["currency"] == currency_name:
            return float(account["available_balance"]["value"])

    return 0


def get_server_timestamp(client: RESTClient):
    data = client.get_unix_time()
    return int(data["epochSeconds"])


def sell_coin(client: RESTClient, coin_name: str, amount: float) -> tuple:
    # Creates a random order ID to use a "primary key"
    order_id = random.randint(0, 1000000000)
    result = client.market_order_sell(
        str(order_id), coin_name, f"{amount:.8f}")

    return (bool(result["success"]), "" if result["success"] == "true" else result["error_response"]["error"])
