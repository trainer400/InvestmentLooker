from configuration_reader import *
from coinbase_interface import *
from investment_strategy import *
from coinbase.rest import RESTClient
import time
import pickle
import sys


def load_internal_state(config: UserConfiguration):
    file_path = get_absolute_path(
        "../internal_states/" + config.LOG_NAME + ".state")
    state = InternalState()
    state.last_action = Action.NONE
    state.last_buy_price = 0
    state.last_action_ts = 0

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


def save_internal_state(config: UserConfiguration, state: InternalState):
    file_path = get_absolute_path(
        "../internal_states/" + config.LOG_NAME + ".state")

    # Create the file
    log = open(file_path, "wb")

    # Save the struct
    pickle.dump(state, log)
    log.close()


def main():
    # Read the user configuration
    configs = read_user_configurations("../invester_config.csv")

    # Delay on startup
    time.sleep(10)

    # Set the std output to a log file
    new_stdout = open(get_absolute_path("../console.log"), "w")
    sys.stdout = new_stdout
    sys.stderr = new_stdout

    # Update loop
    while True:
        for config in configs:
            # Setup the API client
            client = RESTClient(key_file=get_absolute_path(
                "../" + config.KEY_FILE_NAME))

            # Init the internal state
            state = load_internal_state(config)

            try:
                # Update the internal state with fresh data
                state.timestamp = get_server_timestamp(client)
                state.current_price = get_current_price(
                    client, config.COIN_NAME)
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

                    if not config.TEST_MODE:
                        action_result = buy_coin(client, config.COIN_NAME,
                                                 state.current_base_coin_availability)

                    if action_result[0]:
                        # Register the purchase details
                        state.last_buy_price = state.current_price
                        state.last_action = decision
                        state.last_action_ts = state.timestamp

                        # Log the event
                        log_data(get_absolute_path(
                            "../execution_logs/" + config.LOG_NAME + ".ev"), state)
                    else:
                        print(
                            f"[{state.timestamp}][ERR][BUY] Error during buy transaction")

                elif decision == Action.SELL or decision == Action.SELL_LOSS:
                    # Sell coins
                    action_result = (True, "")

                    if not config.TEST_MODE:
                        action_result = sell_coin(client, config.COIN_NAME,
                                                  state.current_coin_availability)

                    if action_result[0]:
                        # Register the sell details
                        state.last_action = decision
                        state.last_action_ts = state.timestamp

                        # Log the event
                        log_data(get_absolute_path(
                            "../execution_logs/" + config.LOG_NAME + ".ev"), state)
                    else:
                        print(
                            f"[{state.timestamp}][ERR][SELL] Error during sell transaction")

                # Save the internal in case of a restart
                save_internal_state(config, state)

                # Log the internal state
                log_data(get_absolute_path(
                    "../execution_logs/" + config.LOG_NAME + ".log"), state)
                print(f"[{state.timestamp}][INFO] Logged data")

                # Flush the console log
                new_stdout.flush()

            except Exception as e:
                print(
                    f"[{state.timestamp}][ERR] Caught unhandled exception during the process: {str(e)}")

        # Sleep until next update
        time.sleep(60)


if __name__ == "__main__":
    main()
