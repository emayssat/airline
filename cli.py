#!/usr/bin/env python3

#%% packages
import sys
import os
import yaml

from airline import Airline
from airplane import Airplane

#%% constants
PROG_NAME = './cli.py'                        # also sys.argv[0] ;-)
DEFAULT_AIRLINE_NAME = "Seattle Airlines"
DEFAULT_AIRPLANE_NAME = "SA101"
DEFAULT_DEBUG = False
DEBUG = os.environ.get("DEBUG", str(DEFAULT_DEBUG)).lower() in ("1", "true", "yes", "on")
stderr = sys.stderr.write

#%% helper functions
def print_usage(active_airline_name, active_airplane_name):
    """Print usage instructions to stderr."""
    stderr(f"-+" * 40 + "\n")
    stderr(f"Usage: {PROG_NAME} [ADD|BOOK|CANCEL|LIST] ...\n")
    stderr(f"Examples:\n")
    stderr(f"  - Add active airplane '{active_airplane_name}' to active airline '{active_airline_name}': {PROG_NAME} ADD\n")
    stderr(f"  - Add a new airplane with default settings: {PROG_NAME} ADD <AIRPLANE_NAME>  [RowCount] [RowLayout]\n")
    stderr(f"  - Book seat A1 on airplane {active_airplane_name}: {PROG_NAME} BOOK A1 1\n")
    stderr(f"  - Book 3 consecutive seats starting at A1 on airplane '{active_airplane_name}': {PROG_NAME} BOOK A1 3\n")
    stderr(f"  - Cancel seat A1 on airplane '{active_airplane_name}': {PROG_NAME} CANCEL A1 1\n")
    stderr(f"  - List all airplanes for airline '{active_airline_name}': {PROG_NAME} LIST\n")
    stderr(f"\n")
    stderr(f"Environment variables:\n")
    stderr(f"  - AIRLINE_NAME: Name of the airline for LIST and ADD commands\n")
    stderr(f"                  default: '{DEFAULT_AIRLINE_NAME}'\n")
    stderr(f"                  active: '{active_airline_name}'\n")
    stderr(f"  - AIRPLANE_NAME: Name of the airplane for BOOK and CANCEL commands\n")
    stderr(f"                   default: '{DEFAULT_AIRPLANE_NAME}'\n")
    stderr(f"                   active: '{active_airplane_name}'\n")
    stderr(f"-+" * 40 + "\n")
    return

def add_airplane(airline, airplane_name, argv):
    """
    Handle the ADD command to create a new airplane.
    Save a snapshot after each successful operation.
    """
    log(f'argv={argv}')

    # Command line validation
    if len(argv) < 2 or len(argv) > 5:
        print_usage(airline.name, airplane_name)
        return

    row_count = 20
    row_layout = "xx_xxxx_xx"

    if len(argv) > 2:
        # If provided, take the airplane name from the command line
        airplane_name = argv[2]
    
    if len(argv) > 3:
        try:
            row_count = int(argv[3])
        except ValueError:
            stderr("Number of rows must be an integer\n")
            return print("FAIL")
    
    if len(argv) > 4:
        row_layout = argv[4]
    
    if airline.add_airplane(airplane_name, row_count, row_layout):
        airline.save_snapshot()
        print("SUCCESS")
    else:
        print("FAIL")

def book_seats(airline, airplane, argv):
    """
    Handle the BOOK command to reserve seats.
    Save a snapshot after each successful operation.
    """
    log(f'argv={argv}')

    # Command line validation
    if len(argv) < 4 or len(argv) > 4:
        print_usage(airline.name, airplane.name)
        return

    seat_name = argv[2]

    try:
        num_seats = int(argv[3])        # convert str to integer
    except ValueError:
        stderr("Number of seats must be an integer\n")
        return print("FAIL")
    
    log(f'airplane.book_seats seat_name={seat_name} num_seats={num_seats}')
    if airplane.book_seats(seat_name, num_seats):
        airline.save_snapshot()
        print("SUCCESS")
    else:
        print("FAIL")

def cancel_seats(airline, airplane, argv):
    """
    Handle the CANCEL command to release seats.
    Save a snapshot after a successful operation.
    """
    log(f'argv={argv}')

    # Command line validation
    if len(argv) < 4 or len(argv) > 4:
        print_usage(airline.name, airplane.name)
        return

    seat_name = argv[2]

    try:
        num_seats = int(argv[3])        # convert str to integer
    except ValueError:
        stderr("Number of seats must be an integer\n")
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
        print(f"[DEBUG] [CLI] {message}", file=sys.stderr)

#%% main function
def main(argv):
    """Entry point of the CLI program."""
    # Get airline/airplane from environment variables or use default values
    airline_name = os.environ.get("AIRLINE_NAME", DEFAULT_AIRLINE_NAME)
    airplane_name = os.environ.get("AIRPLANE_NAME", DEFAULT_AIRPLANE_NAME)
    
    # Initialize the airline company
    airline = Airline(airline_name)
    
    # Load existing snapshot if available, at each command
    airline.load_snapshot()
    
    if len(argv) < 2:
        print_usage(airline_name, airplane_name)
        return
        
    # prog_name = argv[0]
    action = argv[1].upper()
    
    # Handle LIST command - doesn't require an airplane name
    if action == "LIST":
        list_airplanes(airline)
        return
    
    # Handle ADD command which requires an airplane name from the command line
    if action == "ADD":
        add_airplane(airline, airplane_name, argv)
        return
    
    # Get the airplane object
    airplane = airline.get_airplane(airplane_name)
    if not airplane:
        stderr(f"Airplane {airplane_name} not found. Add it first using ADD command.\n")
        print("FAIL")
        return
    
    if action == "BOOK":
        book_seats(airline, airplane, argv)
    elif action == "CANCEL":
        cancel_seats(airline, airplane, argv)
    else:
        stderr(f"Unknown action: {action}\n")
        print("FAIL")

#%% Execution from command line
if __name__ == "__main__":
    main(sys.argv)
