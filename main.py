import model
import inventory_accounting_methods
import sys
from file_reader import *

def main():
    if (len(sys.argv) > 1):
        file_path = sys.argv[1]
    else:
        file_path = "./test_data/trades.csv"
    file_reader = FileReader()
    sorted_trades = file_reader.read_trades(file_path)


if __name__ == "__main__":
    main()