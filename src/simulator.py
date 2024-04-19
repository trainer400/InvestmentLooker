from configuration_reader import *
from investment_strategy import *
from coinbase_interface import *
import matplotlib.pyplot as plt
import datetime as dt
import time

INITIAL_INVESTMENT = 100
LOG_FILE = "../logs/BTC-EUR-1YR.csv"


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
    (data_ts, data_date, data_price) = read_log_file(LOG_FILE)

    # Plot the data
    fig, ax = plt.subplots()
    ax.plot(data_date, data_price)
    plt.show()


if __name__ == "__main__":
    main()
