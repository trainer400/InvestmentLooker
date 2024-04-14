from configuration_reader import *
from coinbase_interface import *
from logger import *
from coinbase.rest import RESTClient
import time


class InternalState(LoggableObject):
    timestamp = 0
    current_price = 0
    current_coin_availability = 0
    current_base_coin_availability = 0
    considered_avg = 0
    last_action = ""
    last_buy_price = 0

# Delay on startup
# time.sleep(10)


config = read_user_configuration("../invester_config.csv")
client = RESTClient(key_file=get_absolute_path("../" + config.KEY_FILE_NAME))

# Init the internal state
state = InternalState()
state.timestamp = 0
state.current_price = 0
state.current_coin_availability = 0
state.current_base_coin_availability = 0
state.considered_avg = 0
state.last_action = ""
state.last_buy_price = 0

# Update loop
while True:
    # Update the internal state with fresh data
    state.timestamp = get_server_timestamp(client)
    state.current_price = get_current_price(client, config.COIN_NAME)
    state.current_coin_availability = get_coin_availability(
        client, config.CURRENCY_NAME)
    state.current_base_coin_availability = get_coin_availability(
        client, config.BASE_CURRENCY_NAME)
    state.considered_avg = get_avg_price(
        client, config.COIN_NAME, config.AVG_HRS)

    # Log the internal state
    log_data(get_absolute_path("../" + config.LOG_NAME), state)
    print(f"[{state.timestamp}][INFO] Logged data")

    # Sleep for a minute
    time.sleep(2)
