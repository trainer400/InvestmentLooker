from pathlib import Path
import matplotlib.pyplot as plt
import datetime as dt
import csv
import os

LOG_FILE = "../execution_logs/AKT.log"


def read_log_file(path: str) -> tuple[list, list, list, list]:
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
    data_avg = []
    data_unix = []
    for row in reader:
        data_ts.append(int(row["timestamp"]))
        data_price.append(float(row["current_price"]))
        data_avg.append(float(row["considered_avg"]))
        data_unix.append(dt.datetime.fromtimestamp(int(row["timestamp"])))

    file.close()
    return (data_ts, data_unix, data_price, data_avg)


def main():
    fig, ax = plt.subplots()

    (data_ts, data_unix, data_price, data_avg) = read_log_file(LOG_FILE)

    ax.plot(data_unix, data_price)
    ax.plot(data_unix, data_avg, color="yellow")
    plt.show()


if __name__ == "__main__":
    main()
