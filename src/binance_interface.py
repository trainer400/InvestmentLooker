from binance.spot import Spot
import math


def truncate(num: float, decimals: int) -> float:
    result = num

    # No negative numbers are accepted
    decimals = abs(decimals)

    # Multiply the value and use math truncate to approximate it
    result = num * pow(10, decimals)
    result = math.trunc(result)

    return float(result) / pow(10, decimals)


def get_current_price(client: Spot, coin_name: str):
    data = client.ticker_price(coin_name)
    return truncate(float(data["price"]), 8)


def get_coin_availability(client: Spot, currency_name: str):
    data = client.account()

    for balance in data["balances"]:
        if balance["asset"] == currency_name:
            amount = float(balance["free"])

            # Approximate in defect the amount (8 decimals)
            return truncate(amount, 8)
    return 0


def get_server_timestamp(client: Spot):
    data = client.time()

    # From milliseconds to seconds (unix time)
    return int(data["serverTime"]) // 1000
