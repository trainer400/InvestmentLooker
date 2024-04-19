from configuration_reader import *
from investment_strategy import *
from coinbase_interface import *
import matplotlib.pyplot as plt
import datetime as dt
import time

INITIAL_INVESTMENT = 100
LOG_FILE = "../logs/SOL-EUR-1YR.csv"
COIN_NAME = "SOL-EUR"
CURRENCY_NAME = "SOL"
BASE_CURRENCY_NAME = "EUR"
AVG_HRS = 48
MIN_GAIN = 5
BUY_TAX = 0.6
SELL_TAX = 0.6
DOUBLE_STRATEGY = 0


def read_log_file(path: str) -> tuple[list, list]:
    # Read the CSV log file
    log_location = Path(__file__).absolute().parent
    file_location = log_location / path

    # Verify the log file presence
    if not os.path.exists(file_location):
        raise Exception("[ERR] The log file does not exist")

    # Open the file
    file = file_location.open()
    reader = csv.DictReader(file)

    # Read the content
    data_ts = []
    data_price = []
    data_unix = []
    for row in reader:
        data_ts.append(int(row["timestamp"]))
        data_price.append(float(row["price"]))
        data_unix.append(dt.datetime.fromtimestamp(int(row["timestamp"])))

    file.close()
    return (data_ts, data_unix, data_price)


def compute_avg_price(data_ts: list, data_price: list, avg_hrs: int, starting_timestamp: int):
    # Delta in seconds that the requested average impacts on the timestamp
    delta_seconds = avg_hrs * 60 * 60

    # Sum all the prices that correspond to a timestamp that is inside the considered average window
    result = 0
    counter = 0
    for i in range(len(data_ts)):
        if data_ts[i] < starting_timestamp and data_ts[i] > starting_timestamp - delta_seconds:
            result += data_price[i]
            counter += 1
        elif data_ts[i] > starting_timestamp:
            break
    return float(result) / counter


def main():
    # Create user configuration
    config = UserConfiguration()
    config.AVG_HRS = AVG_HRS
    config.COIN_NAME = COIN_NAME
    config.CURRENCY_NAME = CURRENCY_NAME
    config.BASE_CURRENCY_NAME = BASE_CURRENCY_NAME
    config.MIN_GAIN = MIN_GAIN
    config.BUY_TAX = BUY_TAX
    config.SELL_TAX = SELL_TAX
    config.DOUBLE_STRATEGY = DOUBLE_STRATEGY

    # Create an internal state to use during the simulation
    state = InternalState()
    state.current_base_coin_availability = INITIAL_INVESTMENT

    # Gather the data
    print("[INFO] Gathering data")
    (data_ts, data_date, data_price) = read_log_file(LOG_FILE)

    # Plot the data
    fig, ax = plt.subplots()
    ax.plot(data_date, data_price)

    # Find the first location in the data which has enough previous samples to compute the average
    starting_index = 0
    first_ts = data_ts[0]
    for i in range(len(data_ts)):
        if data_ts[i] > first_ts + AVG_HRS * 60 * 60:
            starting_index = i
            break

    # Compute the initial average
    state.considered_avg = compute_avg_price(
        data_ts, data_price, AVG_HRS, data_ts[starting_index])

    # Run the simulator
    for i in range(starting_index, len(data_ts)):
        # print(
        #     f"[INFO] Simulation progress: {float(100.0 * (i - starting_index) / (len(data_ts) - starting_index)):.2f}%")

        # Populate the equivalent state
        state.timestamp = data_ts[i]
        state.current_price = data_price[i]

        # Propagate the average by multiplying with the number of considered values, subtracting the
        # first of the previously considered ones and adding the new one
        state.considered_avg = ((state.considered_avg * starting_index) -
                                data_price[i - starting_index] + data_price[i]) / starting_index

        # Make the strategic decision
        decision = make_decision(state, config)

        # Update the internal state
        if decision == Action.BUY:
            investment = state.current_base_coin_availability
            state.last_buy_price = state.current_price
            state.current_coin_availability = (investment -
                                               (BUY_TAX / 100.0) * investment) / state.current_price
            state.current_base_coin_availability = 0
            state.last_action = Action.BUY
            ax.axvline(data_date[i], color="b", label="BUY")

            # Report the buy action
            print(
                f"[{data_date[i]}]BUY action {config.BASE_CURRENCY_NAME}: {investment:.2f} {config.CURRENCY_NAME}: {state.current_coin_availability:.8f}")

        elif decision == Action.SELL:
            investment = state.current_coin_availability
            state.last_action = Action.SELL
            state.current_base_coin_availability = state.current_coin_availability * state.current_price - \
                (config.SELL_TAX / 100.0) * \
                state.current_coin_availability * state.current_price
            state.current_coin_availability = 0
            ax.axvline(data_date[i], color="g", label="SELL")

            # Report the sell action
            print(
                f"[{data_date[i]}]SELL action {config.BASE_CURRENCY_NAME}: {state.current_base_coin_availability:.2f} {config.CURRENCY_NAME}: {investment:.8f}")

    plt.show()


if __name__ == "__main__":
    main()
