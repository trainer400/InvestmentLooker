from coinbase.rest import RESTClient
from json import dumps
import random
import math


def get_current_price(client: RESTClient, coin_name: str):
    data = client.get_product(product_id=coin_name)
    return float(data["price"])


def get_coin_availability(client: RESTClient, currency_name: str):
    data = client.get_accounts()

    for account in data["accounts"]:
        if account["currency"] == currency_name:
            amount = float(account["available_balance"]["value"])

            # Process the amount to truncate instead of approximate
            amount = math.trunc(amount * 100000000) / 100000000
            return amount

    return 0


def get_server_timestamp(client: RESTClient):
    data = client.get_unix_time()
    return int(data["epochSeconds"])


def sell_coin(client: RESTClient, coin_name: str, amount: float) -> tuple:
    # Creates a random order ID to use a "primary key"
    order_id = random.randint(0, 1000000000)

    # Process the amount to truncate instead of approximate
    amount = math.trunc(amount * 100000000) / 100000000

    # Use formatting with 8 decimal values due to avoid scientific notation (8 values is the highest amount the coinbase supports)
    result = client.market_order_sell(
        str(order_id), coin_name, f"{amount:.8f}")

    result_bool = bool(result["success"])
    return (result_bool, ("" if result_bool else result["error_response"]["error"]))


def buy_coin(client: RESTClient, coin_name: str, amount: float) -> tuple:
    # Creates a random order ID to use a "primary key"
    order_id = random.randint(0, 1000000000)

    # Process the amount to truncate instead of approximate
    amount = math.trunc(amount * 100) / 100

    # Use formatting with 8 decimal values due to avoid scientific notation (2 values is the highest amount the coinbase supports)
    result = client.market_order_buy(str(order_id), coin_name, f"{amount:.2f}")

    result_bool = bool(result["success"])
    return (result_bool, ("" if result_bool else result["error_response"]["error"]))
