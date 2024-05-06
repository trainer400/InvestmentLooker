from coinbase.rest import RESTClient
from json import dumps
import random
import math


def truncate(num: float, decimals: int) -> float:
    result = num

    # No negative numbers are accepted
    decimals = abs(decimals)

    # Multiply the value and use math truncate to approximate it
    result = num * pow(10, decimals)
    result = math.trunc(result)

    return float(result) / pow(10, decimals)


def get_increment_from_string(increment: str):
    number = float(increment)

    # The counter is incremented every time we need to remove a 0
    counter = 0
    while number != 1:
        number *= 10
        counter += 1

    return counter


def get_current_price(client: RESTClient, coin_name: str):
    data = client.get_product(product_id=coin_name)
    return truncate(float(data["price"]), 8)


def get_coin_availability(client: RESTClient, currency_name: str):
    data = client.get_accounts()

    for account in data["accounts"]:
        if account["currency"] == currency_name:
            amount = float(account["available_balance"]["value"])

            # Approximate in defect the amount (8 decimals)
            return truncate(amount, 8)

    return 0


def get_server_timestamp(client: RESTClient):
    data = client.get_unix_time()
    return int(data["epochSeconds"])


def get_avg_price(client: RESTClient, coin_name: str, avg_hrs: int, starting_timestamp: int):
    current_time = starting_timestamp
    delta_seconds = avg_hrs * 60 * 60
    data = client.get_candles(
        coin_name, current_time - delta_seconds, current_time, "THIRTY_MINUTE")

    candles = data["candles"]

    # Sum the average among open and close prices
    result = 0.0
    for candle in candles:
        result += (float(candle["open"]) + float(candle["close"])) / 2.0

    # Average the final result
    result = result / len(candles)

    return truncate(result, 8)


def sell_coin(client: RESTClient, coin_name: str, amount: float) -> tuple:
    product_details = client.get_product(product_id=coin_name)

    # Get maximum precision that the API accepts for the coin
    increment = get_increment_from_string(product_details["base_increment"])

    # Creates a random order ID to use a "primary key"
    order_id = random.randint(0, 1000000000)

    # Process the amount to truncate instead of approximate
    amount = truncate(amount, increment)

    # Use formatting with "increment" decimal values due to avoid scientific notation (8 values is the highest amount the coinbase supports)
    result = client.market_order_sell(
        str(order_id), coin_name, f"{amount:.8f}")

    result_bool = bool(result["success"])
    return (result_bool, ("" if result_bool else (result["error_response"]["error"] + "," + result["error_response"]["message"])))


def buy_coin(client: RESTClient, coin_name: str, amount: float) -> tuple:
    # Creates a random order ID to use a "primary key"
    order_id = random.randint(0, 1000000000)

    # Process the amount to truncate instead of approximate
    amount = truncate(amount, 2)

    # Use formatting with 2 decimal values due to avoid scientific notation (2 values is the highest amount the coinbase supports)
    result = client.market_order_buy(str(order_id), coin_name, f"{amount:.2f}")

    result_bool = bool(result["success"])
    return (result_bool, ("" if result_bool else (result["error_response"]["error"] + "," + result["error_response"]["message"])))
