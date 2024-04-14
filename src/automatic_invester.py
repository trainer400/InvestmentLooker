from configuration_reader import *
from coinbase_interface import *
from automatic_invester import *
from investment_strategy import *
from coinbase.rest import RESTClient
import time
import pickle


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
    # Delay on startup
    time.sleep(10)

    config = read_user_configuration("../invester_config.csv")
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
                client, config.COIN_NAME, config.AVG_HRS)

            # Make decision
            decision = make_decision(state, config)

            # Actuate the decision
            if decision == Action.BUY:
                # Buy coins
                buy_coin(client, config.COIN_NAME,
                         state.current_base_coin_availability)

                # Register the purchase details
                state.last_buy_price = state.current_price
                state.last_action = Action.BUY

                print("[INFO][BUY] Bought coin: " +
                      f"{state.current_base_coin_availability:.2f}" + " " + config.BASE_CURRENCY_NAME)

                # Log the event
                log_data(get_absolute_path(
                    "../" + config.LOG_NAME + ".ev"), state)

            elif decision == Action.SELL:
                # Sell coins
                sell_coin(client, config.COIN_NAME,
                          state.current_coin_availability)

                # Register the sell details
                state.last_action = Action.SELL

                print("[INFO][SELL] Sold coin: " +
                      f"{state.current_coin_availability:.8}" + " " + config.CURRENCY_NAME)

                # Log the event
                log_data(get_absolute_path(
                    "../" + config.LOG_NAME + ".ev"), state)

            # Save the internal in case of a restart
            save_internal_state(state)

            # Log the internal state
            log_data(get_absolute_path("../" + config.LOG_NAME), state)
            print(f"[{state.timestamp}][INFO] Logged data")

            # Sleep for a minute
            time.sleep(5)
        except:
            print("[ERR] Caught unhandled exception during the process")


if __name__ == "__main__":
    main()
