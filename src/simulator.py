from configuration_reader import *
from investment_strategy import *
from coinbase_interface import *
import time

INITIAL_INVESTMENT = 100
SIMULATION_DAYS = 10


def get_simulation_data(client: RESTClient, coin_name: str, starting_timestamp: int):
    # A max of 300 samples can be requested
    current_time = starting_timestamp
    delta_seconds = 300 * 60

    iterations = SIMULATION_DAYS * 24.0 * 60.0 / 300.0
    counter = 0
    while counter < iterations:
        try:
            counter += 1
        except Exception as e:
            print(f"[ERR] Error retrieving simulation data: {str(e)}")
            time.sleep(1)


def main():
    # Read the user configuration
    config = read_user_configuration("../invester_config.csv")

    # Create an internal state to use during the simulation
    state = InternalState()
    state.current_base_coin_availability = INITIAL_INVESTMENT

    # Setup the API client
    client = RESTClient(key_file=get_absolute_path(
        "../" + config.KEY_FILE_NAME))


if __name__ == "__main__":
    main()
