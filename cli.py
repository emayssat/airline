#!/usr/bin/env python3

#%% packages
import sys
import os
import yaml

from airline import Airline
from airplane import Airplane

#%% constants
PROG_NAME = './cli.py'
DEFAULT_AIRLINE_NAME = "Seattle Airlines"
DEFAULT_AIRPLANE_NAME = "SA101"
DEFAULT_DEBUG = False
DEBUG = os.environ.get("DEBUG", str(DEFAULT_DEBUG)).lower() in ("1", "true", "yes", "on")

#%% helper functions
def print_usage(active_airline_name, active_airplane_name):
    """Print usage instructions to stderr."""
    sys.stderr.write("-+" * 40 + "\n")
    sys.stderr.write(f"Usage: {PROG_NAME} [BOOK|CANCEL|ADD|LIST] ...\n")
    sys.stderr.write("Examples:\n")
    sys.stderr.write(f"  - Book seat A1 on airplane {active_airplane_name}: {PROG_NAME} BOOK A1\n")
    sys.stderr.write(f"  - Book 3 consecutive seats starting at A1 on airplane '{active_airplane_name}': {PROG_NAME} BOOK A1 3\n")
    sys.stderr.write(f"  - Cancel seat A1 on airplane '{active_airplane_name}': {PROG_NAME} CANCEL A1\n")
    sys.stderr.write(f"  - Add a new airplane with default settings: {PROG_NAME} ADD <AIRPLANE_NAME>  [RowCount] [RowLayout]\n")
    sys.stderr.write(f"  - List all airplanes for airline '{active_airline_name}': {PROG_NAME} LIST\n")
    sys.stderr.write("\n")
    sys.stderr.write("Environment variables:\n")
    sys.stderr.write(f"  - AIRLINE_NAME: Name of the airline\n")
    sys.stderr.write(f"                  default: '{DEFAULT_AIRLINE_NAME}'\n")
    sys.stderr.write(f"                  active: '{active_airline_name}'\n")
    sys.stderr.write(f"  - AIRPLANE_NAME: Name of the airplane for BOOK and CANCEL commands\n")
    sys.stderr.write(f"                   default: '{DEFAULT_AIRPLANE_NAME}'\n")
    sys.stderr.write(f"                   active: '{active_airplane_name}'\n")

    sys.stderr.write("-+" * 40 + "\n")
    return

def add_airplane(airline, airplane_name, argv):
    """Handle the ADD command to create a new airplane."""
    row_count = 20
    row_layout = "xx_xxxx_xx"
    
    if len(argv) > 3:
        try:
            row_count = int(argv[3])
        except ValueError:
            sys.stderr.write("Number of rows must be an integer\n")
            return print("FAIL")
    
    if len(argv) > 4:
        row_layout = argv[4]
    
    if airline.add_airplane(airplane_name, row_count, row_layout):
        airline.save_snapshot()
        print("SUCCESS")
    else:
        print("FAIL")

def book_seats(airline, airplane, argv):
    """Handle the BOOK command to reserve seats."""
    log(f'argv={argv}')
    seat_name = argv[2]

    try:
        num_seats = int(argv[3])        # convert str to integer
    except ValueError:
        sys.stderr.write("Number of seats must be an integer\n")
        return print("FAIL")
    
    log(f'airplane.book_seats seat_name={seat_name} num_seats={num_seats}')
    if airplane.book_seats(seat_name, num_seats):
        airline.save_snapshot()
        print("SUCCESS")
    else:
        print("FAIL")

def cancel_seats(airline, airplane, argv):
    """Handle the CANCEL command to release seats."""
    log(f'argv={argv}')
    seat_name = argv[2]

    if len(argv) < 3:
        print_usage()
        return

    if len(argv) > 3:
        try:
            num_seats = int(argv[3])        # convert str to integer
        except ValueError:
            sys.stderr.write("Number of seats must be an integer\n")
            return print("FAIL")

    log(f'airplane.cancel_seats seat_name={seat_name} num_seats={num_seats}')    
    if airplane.cancel_seats(seat_name, num_seats):
        airline.save_snapshot()
        print("SUCCESS")
    else:
        print("FAIL")

def list_airplanes(airline):
    """Handle the LIST command to display all airplanes."""
    airplane_names = airline.get_airplane_names()
    
    if not airplane_names:
        print("No airplanes found.")
        return
    
    print(f"Airplanes for {airline.name}:")
    for name in airplane_names:
        print(f"- {name}")
    
    print(f"Total: {len(airplane_names)} airplane(s)")

def log(message):
    """Prints debug messages if debugging is enabled."""
    if DEBUG:
        print(f"[DEBUG] [CLI] {message}")

#%% main function
def main(argv):
    """Entry point of the CLI program."""
    # Get airline/airplane from environment variables or use default values
    airline_name = os.environ.get("AIRLINE_NAME", DEFAULT_AIRLINE_NAME)
    airplane_name = os.environ.get("AIRPLANE_NAME", DEFAULT_AIRPLANE_NAME)
    
    # Initialize the airline company
    airline = Airline(airline_name)
    
    # Load existing data if available
    airline.load_snapshot()
    
    if len(argv) < 2:
        print_usage(airline_name, airplane_name)
        return
        
    action = argv[1].upper()
    
    # Handle LIST command - doesn't require an airplane name
    if action == "LIST":
        list_airplanes(airline)
        return
    
    # Handle ADD command which requires an airplane name from the command line
    if action == "ADD":
        if len(argv) < 3:
            print_usage(airline_name, airplane_name)
            return
        # Use the airplane name from command line for ADD
        cmd_airplane_name = argv[2]
        add_airplane(airline, cmd_airplane_name, argv)
        return
    
    # Get the airplane object
    airplane = airline.get_airplane(airplane_name)
    if not airplane:
        sys.stderr.write(f"Airplane {airplane_name} not found. Add it first using ADD command.\n")
        print("FAIL")
        return
    
    if action == "BOOK":
        if len(argv) < 4:
            print_usage()
            return
        book_seats(airline, airplane, argv)
    elif action == "CANCEL":
        if len(argv) < 3:
            print_usage()
            return
        cancel_seats(airline, airplane, argv)
    else:
        sys.stderr.write(f"Unknown action: {action}\n")
        print("FAIL")

#%% Execution from command line
if __name__ == "__main__":
    main(sys.argv)
