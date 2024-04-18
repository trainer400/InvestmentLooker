from configuration_reader import *
from investment_strategy import *
from coinbase_interface import *
import matplotlib.pyplot as plt
import datetime as dt
import time

INITIAL_INVESTMENT = 100
SIMULATION_DAYS = 30


def get_simulation_data(client: RESTClient, coin_name: str, starting_timestamp: int):
    # A max of 300 samples can be requested
    current_time = starting_timestamp
    delta_seconds = 300 * 60
    iterations = int(SIMULATION_DAYS * 24.0 * 60.0 / 300.0)

    data_collection_ts = []
    data_collection_price = []

    counter = 0
    while counter < iterations:
        try:
            print(
                f"[INFO] Data gathering: {(100.0 * counter / iterations):.2f}%")
            # Retrieve the data candles
            data = client.get_candles(
                coin_name, current_time - (iterations - counter) * delta_seconds, current_time - (iterations - counter - 1) * delta_seconds, "ONE_MINUTE")

            # Pack them from top to bottom (the candles are sorted such that the most recent time is the first element)
            for i in range(len(data["candles"])):
                candle = data["candles"][len(data["candles"]) - 1 - i]
                data_collection_ts.append(
                    dt.datetime.fromtimestamp(int(candle["start"])))
                data_collection_price.append(float(candle["open"]))

            counter += 1
        except Exception as e:
            print(f"[ERR] Error retrieving simulation data: {str(e)}")
            time.sleep(1)

    return (data_collection_ts, data_collection_price)


def main():
    # Read the user configuration
    config = read_user_configuration("../invester_config.csv")

    # Create an internal state to use during the simulation
    state = InternalState()
    state.current_base_coin_availability = INITIAL_INVESTMENT

    # Setup the API client
    client = RESTClient(key_file=get_absolute_path(
        "../" + config.KEY_FILE_NAME))

    # Gather the data
    print("[INFO] Gathering data")
    (data_ts, data_price) = get_simulation_data(
        client, config.COIN_NAME, get_server_timestamp(client))

    # Plot the data
    fig, ax = plt.subplots()
    ax.plot(data_ts, data_price)
    plt.show()


if __name__ == "__main__":
    main()
