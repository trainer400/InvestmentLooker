from configuration_reader import *
from investment_strategy import *
from coinbase_interface import *

INITIAL_INVESTMENT = 100


def main():
    # Read the user configuration
    config = read_user_configuration("../invester_config.csv")

    # Create an internal state to use during the simulation
    state = InternalState()
    state.current_base_coin_availability = INITIAL_INVESTMENT


if __name__ == "__main__":
    main()
