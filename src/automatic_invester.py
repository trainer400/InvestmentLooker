from configuration_reader import *
from coinbase_interface import *
from coinbase.rest import RESTClient
import time

# Delay on startup
# time.sleep(10)

config = read_user_configuration("../invester_config.csv")
client = RESTClient(key_file=get_absolute_path("../" + config.KEY_FILE_NAME))

while (True):
    print(get_current_price(client, config.COIN_NAME))
    time.sleep(1)
