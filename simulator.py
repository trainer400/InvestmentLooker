from requests import *
import json
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
from enum import Enum


class Action(Enum):
    NONE = 0
    BUY = 1
    SELL = 2


class Configuration:
    COIN_NAME = "BTCEUR"
    INITIAL_INVESTMENT = 0
    AVG_HRS = 24
    MIN_GAIN = 3  # [%]
    BUY_TAX = 0.6  # [%]
    SELL_TAX = 0.6  # [%]


class InternalState:
    current_day = dt.datetime.now()
    current_balance = 0.0
    current_bitcoins = 0.0       # Indicates also if there the last purchase is valid
    last_purchase_day = dt.datetime.now()
    last_purchase_price = 0.0       # Buying price
    last_purchase_amount = 0.0       # Amount bought


def gather_data(coin_name, interval):
    SYMBOL = coin_name
    ROOT_URL = "https://api.binance.com/api/v1/klines"

    # Make the web request
    request = get(ROOT_URL, params={"interval": interval, "symbol": SYMBOL})

    # Extrapolate the data
    raw_data = json.loads(request.text)
    data = pd.DataFrame(raw_data)

    # Set the indices for the data
    data.columns = ['open_time', 'o', 'h', 'l', 'c', 'v', 'close_time',
                    'qav', 'num_trades', 'taker_base_vol', 'taker_quot_vol', 'ignore']
    data.index = [dt.datetime.fromtimestamp(x/1000.0) for x in data.close_time]

    return data


def make_decision(state: InternalState, config: Configuration,  current_price: float, avg_price: float):
    # The user has bitcoins in its account
    if state.current_bitcoins != 0:
        # If the expected gain is greater than the threshold, suggest to sell
        if (1 - (state.last_purchase_price / current_price)) > (config.MIN_GAIN / 100.0):
            return Action.SELL
        # If the price is dropping to much (over 15%) sell in loss
        elif(current_price/state.last_purchase_price) < 0.85:
            return Action.SELL
    elif current_price < (avg_price - avg_price * ((config.BUY_TAX + config.SELL_TAX) / 100.0)):
        return Action.BUY

    return Action.NONE

# Simulation function that is called when this file is executed as main entrypoint


def simulate():
    state = InternalState()
    state.current_balance = 50

    config = Configuration()
    config.COIN_NAME = "BTCEUR"

    precise_data = gather_data(config.COIN_NAME, "1m")
    granular_data = gather_data(config.COIN_NAME, "1h")
    current_price = float(precise_data.c.iloc[len(precise_data.index) - 1])

    granular_data.c.astype('float').plot()

    # Feed the algorithm with past data to benchmark it
    starting_time = granular_data.index[0]

    # Keep track of days
    days = 0

    while (starting_time < dt.datetime.now()):
        days = days + 1
        print("Day #" + str(days))

        # Set the current day that we are evaluating
        current_day = (starting_time + dt.timedelta(hours=config.AVG_HRS))
        print("DAY: " + str(current_day))

        # Interrogate the algorithm on every current price for the day
        for i in range(len(granular_data.index)):
            date = dt.datetime.fromtimestamp(
                granular_data.close_time.iloc[i] / 1000.0)
            state.current_day = date

            if(date.day == current_day.day and date.month == current_day.month):
                current_price = float(granular_data.c.iloc[i])

                # Compute the average
                prices = []
                for j in range(len(granular_data.index)):
                    d = dt.datetime.fromtimestamp(
                        granular_data.close_time.iloc[j] / 1000.0)
                    # TODO Very inefficient
                    if d >= starting_time and d <= date:
                        prices.append(float(granular_data.c.iloc[j]))
                        # print(str(d) + " " + granular_data.c.iloc[i])

                if(len(prices) == 0):
                    continue

                avg_price = sum(prices) / len(prices)

                action = make_decision(state, config, current_price, avg_price)

                if action == Action.BUY and state.current_balance > 0:
                    # Select the amount to buy
                    amount = state.current_balance

                    # Update the internal state
                    state.current_balance -= amount
                    state.current_bitcoins += (amount -
                                               (config.BUY_TAX / 100.0) * amount) / current_price

                    # Update last purchase info
                    state.last_purchase_price = current_price
                    state.last_purchase_amount = amount
                    state.last_purchase_day = date

                    # Draw buy line
                    plt.axvline(
                        x=granular_data.index[i], color='b', label='BUY')

                    # Report the buy action
                    print("BUY action AMOUNT: " + str(amount) + "$ BTC: " +
                          str(state.current_bitcoins) + "B PRICE: " + str(state.last_purchase_price))
                elif action == Action.SELL:
                    # Update the internal state
                    amount = state.current_bitcoins * current_price
                    state.current_balance += amount - \
                        (config.SELL_TAX / 100.0) * amount
                    state.current_bitcoins = 0

                    # Draw sell line
                    plt.axvline(
                        x=granular_data.index[i], color='g', label='SELL')

                    # Report the sell action
                    print("SELL action BALANCE: " + str(state.current_balance) +
                          "$ PRICE: " + str(current_price))

        # At the end update the start time incrementing the day
        starting_time = starting_time + dt.timedelta(1)

    # Sell the remaining at the end of simulation
    if state.current_bitcoins != 0:
        # Update the internal state
        amount = state.current_bitcoins * current_price
        state.current_balance += amount - (config.SELL_TAX / 100.0) * amount
        state.current_bitcoins = 0

        # Report the sell action
        print("SELL action BALANCE: " + str(state.current_balance) +
              "$ PRICE: " + str(current_price))

    # Report the sell action
    print("BALANCE: " + str(state.current_balance))

    plt.show()


if __name__ == "__main__":
    simulate()
