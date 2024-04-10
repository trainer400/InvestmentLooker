from pathlib import Path
import datetime as dt
import tkinter
import time
import csv
import pickle
import os
import simulator

def create_new_log_file(name):
    # Create the file
    log = open(name, "wb")

    # Save a new void structure inside
    voidState = simulator.InternalState()
    pickle.dump(voidState, log)
    log.close()

    # Print the action
    print("[INFO] Created new log file: " + str(name))

def evaluate_investment(config : simulator.Configuration, state : simulator.InternalState):
    # Gather the necessary data to evaluate the investments
    precise_data = simulator.gather_data(config.COIN_NAME, "1m")
    granular_data = simulator.gather_data(config.COIN_NAME, "30m")
    current_price = float(precise_data.c.iloc[len(precise_data.index) - 1])

    # Define the current date
    current_date = dt.datetime.fromtimestamp(precise_data.close_time.iloc[len(precise_data.index) - 1] / 1000.0)

    # Compute the average
    prices = []
    for j in range(len(granular_data.index)):
        # Data reference date
        date = dt.datetime.fromtimestamp(granular_data.close_time.iloc[j] / 1000.0)

        # In case inside the user defined window, count it
        if date > current_date - dt.timedelta(hours=int(config.AVG_HRS)):
            prices.append(float(granular_data.c.iloc[j]))
            # print(str(date) + " " + granular_data.c.iloc[j])
    
    avg_price = sum(prices) / len(prices)

    # Evaluate the situation
    action = simulator.make_decision(state, config, current_price, avg_price)
    print(str(action) + " " + str(avg_price) + " " + str(current_price))



# Create the notify window
window = tkinter.Tk()
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

        # Check that the log file exists
        if(not os.path.isfile(script_location / row["LOG_NAME"])):
            create_new_log_file(row["LOG_NAME"])

            # Avoid the current step
            continue

        # Load the log file
        log = open(row["LOG_NAME"], "rb")
        state = pickle.load(log)
        log.close()

        # Populate the configuration
        config = simulator.Configuration()
        config.COIN_NAME = row["COIN_NAME"]
        config.AVG_HRS = int(row["AVG_HRS"])
        config.MIN_GAIN = float(row["MIN_GAIN"])
        config.BUY_TAX = float(row["BUY_TAX"])
        config.SELL_TAX = float(row["SELL_TAX"])

        # Evaluate the current investment
        evaluate_investment(config, state)


    # Sleep for some time
    time.sleep(1)