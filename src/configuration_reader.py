from pathlib import Path
import csv
import os


class UserConfiguration:
    COIN_NAME = ""
    AVG_HRS = 0
    MIN_GAIN = 0.0
    BUY_TAX = 0.0
    SELL_TAX = 0.0
    DOUBLE_STRATEGY = False
    KEY_FILE_NAME = ""
    LOG_NAME = ""


def read_user_configuration(path: str):
    # Read the CSV configuration file
    script_location = Path(__file__).absolute().parent
    file_location = script_location / path

    # Verify the configuration file presence
    if not os.path.exists(file_location):
        raise Exception("[ERR] The configuration file does not exist")

    file = file_location.open()
    reader = csv.DictReader(file)

    # Read all the csv rows
    rows = []
    for row in reader:
        rows.append(row)

    # Check the presence of a valid config row
    if len(rows) < 1:
        raise Exception("[ERR] No valid configuration")

    # Populate the resulting configuration
    row = rows[0]
    config = UserConfiguration()
    config.COIN_NAME = row["COIN_NAME"]
    config.AVG_HRS = int(row["AVG_HRS"])
    config.MIN_GAIN = float(row["MIN_GAIN"])
    config.BUY_TAX = float(row["BUY_TAX"])
    config.SELL_TAX = float(row["SELL_TAX"])
    config.DOUBLE_STRATEGY = False if row["DOUBLE_STRATEGY"] == '0' else True
    config.KEY_FILE_NAME = row["KEY_FILE_NAME"]
    config.LOG_NAME = row["LOG_NAME"]

    return config
