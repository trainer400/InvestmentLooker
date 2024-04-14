from pathlib import Path
import datetime as dt
import matplotlib.pyplot as plt
from tkinter import *
from tkinter import messagebox
import time
import csv
import pickle
import os
import simulator


def create_new_log_file(name, config: simulator.Configuration):
    # Create the file
    log = open(name, "wb")

    # Create a new initial struct
    initialState = simulator.InternalState()

    # Populate the struct with the initial values
    initialState.current_balance = float(config.INITIAL_INVESTMENT)

    # Save the struct
    pickle.dump(initialState, log)
    log.close()

    # Print the action
    print("[INFO] Created new log file: " + str(name))


def evaluate_investment(config: simulator.Configuration, state: simulator.InternalState, precise_data, granular_data):
    # Take the last precise data price as current one
    current_price = float(precise_data.c.iloc[len(precise_data.index) - 1])

    # Define the current date
    current_date = dt.datetime.fromtimestamp(
        precise_data.close_time.iloc[len(precise_data.index) - 1] / 1000.0)

    # Compute the average
    prices = []
    for j in range(len(granular_data.index)):
        # Data reference date
        date = dt.datetime.fromtimestamp(
            granular_data.close_time.iloc[j] / 1000.0)

        # In case inside the user defined window, count it
        if date > current_date - dt.timedelta(hours=int(config.AVG_HRS)):
            prices.append(float(granular_data.c.iloc[j]))
            # print(str(date) + " " + granular_data.c.iloc[j])

    avg_price = sum(prices) / len(prices)

    # Evaluate the situation
    action = simulator.make_decision(state, config, current_price, avg_price)
    # print(str(action) + " " + str(avg_price) + " " + str(current_price))
    return action


def show_ui(action: simulator.Action, config: simulator.Configuration, state: simulator.InternalState, precise_data, granular_data):
    result = False
    current_price = float(precise_data.c.iloc[len(precise_data.index) - 1])

    # Depending on the action, suggest to the user what to do
    if action == simulator.Action.BUY:
        # Graph the last price fluctuations
        granular_data.c.astype('float').plot()

        # Graph the buy action
        plt.axvline(x=granular_data.index[len(
            granular_data.index) - 1], color='b', label='BUY')
        plt.show()

        # Ask the user to perform the operation
        result = messagebox.askokcancel("Buy operation", "Cost: {cost:.2f}\nPrice: {price:.2f}\nBTC: {btc:.6f}".format(
            cost=state.current_balance, price=current_price, btc=(state.current_balance - config.BUY_TAX * state.current_balance)/current_price))

    elif action == simulator.Action.SELL:
        # Graph the last price fluctuations
        granular_data.c.astype('float').plot()

        # Draw sell line
        plt.axvline(x=granular_data.index[len(
            granular_data.index) - 1], color='g', label='SELL')
        plt.show()

        # Ask the user to perform the operation
        result = messagebox.askokcancel("Sell operation", "Gain: {gain:.2f}\nPrice: {price:.2f}\nBTC: {btc:.6f}".format(
            gain=(state.current_bitcoins - config.SELL_TAX * state.current_bitcoins) * current_price, price=current_price, btc=state.current_bitcoins))

    return result


# Create the notify window
window = Tk()
window.wm_withdraw()

# Wait 10 seconds to establish internet connection
# time.sleep(10)

while True:
    # Read the CSV file
    script_location = Path(__file__).absolute().parent
    file_location = script_location / 'investments.csv'
    file = file_location.open()
    reader = csv.DictReader(file)

    # Acquire all the csv data
    rows = []
    for row in reader:
        rows.append(row)

    # Close the file
    file.close()

    # Run the decision maker for every row
    for row in rows:
        # Populate the configuration
        config = simulator.Configuration()
        config.COIN_NAME = row["COIN_NAME"]
        config.INITIAL_INVESTMENT = row["INITIAL_INVESTMENT"]
        config.AVG_HRS = int(row["AVG_HRS"])
        config.MIN_GAIN = float(row["MIN_GAIN"])
        config.BUY_TAX = float(row["BUY_TAX"])
        config.SELL_TAX = float(row["SELL_TAX"])

        # Check that the log file exists
        if (not os.path.isfile(script_location / row["LOG_NAME"])):
            create_new_log_file(row["LOG_NAME"], config)

            # Avoid the current step
            continue

        # Load the log file
        log = open(row["LOG_NAME"], "rb")
        state = pickle.load(log)
        log.close()

        # Gather the necessary data to evaluate the investments
        precise_data = simulator.gather_data(config.COIN_NAME, "1m")
        granular_data = simulator.gather_data(config.COIN_NAME, "1h")

        # Evaluate the current investment
        action = evaluate_investment(
            config, state, precise_data, granular_data)
        show_ui(simulator.Action.BUY, config,
                state, precise_data, granular_data)

    # Sleep for some time
    time.sleep(1)
