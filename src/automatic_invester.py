from configuration_reader import *
from coinbase_interface import *
from investment_strategy import *
from coinbase.rest import RESTClient
import time
import pickle
import sys


def load_internal_state():
    file_path = get_absolute_path("../internal_state.log")
    state = InternalState()
    state.last_action = Action.NONE
    state.last_buy_price = 0

    # If the file does not exist, return the default internal state
    if not os.path.exists(file_path):
        print("[INFO] Non pre existing internal state log file, returning default one")
        return state

    # Open the binary file
    log = open(file_path, "rb")

    # Load the binary state
    state = pickle.load(log)
    log.close()

    return state


def save_internal_state(state: InternalState):
    file_path = get_absolute_path("../internal_state.log")

    # Create the file
    log = open(file_path, "wb")

    # Save the struct
    pickle.dump(state, log)
    log.close()


def main():
    # Read the user configuration
    config = read_user_configuration("../invester_config.csv")

    # Delay on startup
    if not config.TEST_MODE:
        time.sleep(10)

    new_stdout = open(get_absolute_path("../console.log"), "w")
    # Change the standard output file if not in test mode
    if not config.TEST_MODE:
        # Set the std output to a log file
        sys.stdout = new_stdout
        sys.stderr = new_stdout

    # Setup the API client
    client = RESTClient(key_file=get_absolute_path(
        "../" + config.KEY_FILE_NAME))

    # Init the internal state
    state = load_internal_state()

    # Update loop
    while True:
        try:
            # Update the internal state with fresh data
            state.timestamp = get_server_timestamp(client)
            state.current_price = get_current_price(client, config.COIN_NAME)
            state.current_coin_availability = get_coin_availability(
                client, config.CURRENCY_NAME)
            state.current_base_coin_availability = get_coin_availability(
                client, config.BASE_CURRENCY_NAME)
            state.considered_avg = get_avg_price(
                client, config.COIN_NAME, config.AVG_HRS, state.timestamp)

            # Make decision
            decision = make_decision(state, config)

            # Actuate the decision
            if decision == Action.BUY:
                # Buy coins
                action_result = (True, "")
                if config.TEST_MODE:
                    print(f"[{state.timestamp}][INFO] Buy action in test mode")
                else:
                    action_result = buy_coin(client, config.COIN_NAME,
                                             state.current_base_coin_availability)

                if action_result[0]:
                    # Register the purchase details
                    state.last_buy_price = state.current_price
                    state.last_action = Action.BUY

                    print(f"[{state.timestamp}][INFO][BUY] Bought coin: " +
                          f"{state.current_base_coin_availability:.2f}" + " " + config.BASE_CURRENCY_NAME)

                    # Log the event
                    log_data(get_absolute_path(
                        "../" + config.LOG_NAME + ".ev"), state)
                else:
                    print(
                        f"[{state.timestamp}][ERR][BUY] Error during buy transaction")

            elif decision == Action.SELL:
                # Sell coins
                action_result = (True, "")
                if config.TEST_MODE:
                    print(f"[{state.timestamp}][INFO] Sell action in test mode")
                else:
                    action_result = sell_coin(client, config.COIN_NAME,
                                              state.current_coin_availability)

                if action_result[0]:
                    # Register the sell details
                    state.last_action = Action.SELL

                    print(f"[{state.timestamp}][INFO][SELL] Sold coin: " +
                          f"{state.current_coin_availability:.8}" + " " + config.CURRENCY_NAME)

                    # Log the event
                    log_data(get_absolute_path(
                        "../" + config.LOG_NAME + ".ev"), state)
                else:
                    print(
                        f"[{state.timestamp}][ERR][SELL] Error during sell transaction")

            # Save the internal in case of a restart
            save_internal_state(state)

            # Log the internal state
            log_data(get_absolute_path("../" + config.LOG_NAME), state)
            print(f"[{state.timestamp}][INFO] Logged data")

            # Flush the console log
            new_stdout.flush()

            # Sleep for a minute
            time.sleep(60)
        except Exception as e:
            print(
                f"[{state.timestamp}][ERR] Caught unhandled exception during the process: {str(e)}")


if __name__ == "__main__":
    main()
