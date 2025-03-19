#%% packages
import os
import sys

#%% constants
DEFAULT_DEBUG=False

#%% Airplane class definition
class Airplane:
    def __init__(self, name, row_count=20, row_layout='xx_xxxx_xx'):
        """
        Initialize an Airplane object.
        Args:
            name (str): Unique identifier for the airplane
            row_count (int): Number of rows in the airplane
            row_layout (str): Seat layout pattern where 'x' represents a seat 
        Example:
            >>> plane = Airplane("TA101", 2, "xx_xxxx_xx")
            >>> plane.name
            'TA101'
            >>> plane.row_count
            2
            >>> plane.seats_per_row
            8
            >>> plane.row_layout
            'xx_xxxx_xx'
        """
        self.debug = os.environ.get("DEBUG", str(DEFAULT_DEBUG)).lower() in ("1", "true", "yes", "on")
        self.log(f'__init__ name={name} row_count={row_count} row_layout={row_layout}')
        self._name = name            # private attribute
        self.row_count = row_count
        self.row_layout = row_layout
        # Number of usable seats per row according to the layout
        self.seats_per_row = sum(1 for c in row_layout if c == 'x')
        # set of reserved seats
        self.reserved_seats = set()

    @property
    def name(self):
        """
        Getter for the name of the airplane

        Example:
            >>> plane = Airplane("TA101")
            >>> plane.name
            'TA101'
        """
        return self._name
    
    @name.setter
    def name(self, new_name):
        """
        Setter for the name of the airplane with validation
        
        Example:
            >>> plane = Airplane("TA101")
            >>> plane.name = "TA202"
            >>> plane.name
            'TA202'
        """
        if not isinstance(new_name, str) or not new_name.strip():
            raise ValueError("Airplane name must be a non-empty string.")
        self._name = new_name

    def get_seat_name(self, row_idx, pos_idx):
        """
        Convert row and position indices to seat name (e.g., A5).
        Args:
            row_idx (int): Zero-based row index
            pos_idx (int): Zero-based position within the row
        Returns:
            str: Seat name in format [ROW_LETTER][POSITION]
            
        Example:
            >>> plane = Airplane("TA101")
            >>> plane.get_seat_name(0, 5)
            'A5'
            >>> plane.get_seat_name(2, 9)
            'C9'
        """
        self.log(f'get_seat_name row_idx={row_idx} pos_idx={pos_idx}')
        return chr(ord('A') + row_idx) + str(pos_idx)
        # return chr(ord('A') + row_idx) + str(pos_idx + 1)    # Add 1 to convert from 0-based to 1-based

    def check_consecutive_seats(self, start_seat_name, num_seats):
        """
        Check if consecutive seats are available.
        Args:
            start_seat_name (str): Starting seat name
            num_seats (int): Number of consecutive seats needed
        Returns:
            bool: True if seats are available, False otherwise
            
        Example:
            >>> plane = Airplane("TA101", 2, "xx_xxxx_xx")
            >>> plane.check_consecutive_seats("A1", 3)
            True
            >>> plane.check_consecutive_seats("A0", 8)
            True
            >>> plane.reserved_seats.add("A1")
            >>> plane.check_consecutive_seats("A1", 3)
            False
            >>> plane.check_consecutive_seats("A3", 5)
            True
            >>> plane.check_consecutive_seats("A9", 2)
            False
        """
        self.log(f'check_consecutive_seats start_seat_name={start_seat_name} num_seats={num_seats}')

        if len(start_seat_name) < 2:
            return False
            
        start_row_idx = ord(start_seat_name[0]) - ord('A')
        try:
            # substract 1 to convert from 1-based to 0-based
            start_pos_idx = int(start_seat_name[1:]) # - 1
        except ValueError:
            return False
        
        # Check if all requested seats are in the same row and within bounds
        if start_row_idx < 0 or start_row_idx >= self.row_count or start_pos_idx < 0 or start_pos_idx + num_seats > self.seats_per_row:
            return False
        
        # Check if all seats are available
        for i in range(num_seats):
            seat_name = self.get_seat_name(start_row_idx, start_pos_idx + i)
            if seat_name in self.reserved_seats:
                return False
                
        return True

    def book_seats(self, start_seat_name, num_seats=1):
        """
        Book consecutive seats.
        Args:
            start_seat (str): Starting seat name
            num_seats (int, optional): Number of consecutive seats to book. Defaults to 1.
        Returns:
            bool: True if booking was successful, False otherwise
            
        Example:
            >>> plane = Airplane("TA101", 2, "xxxx")
            >>> plane.book_seats("A1", 2)
            True
            >>> sorted(list(plane.reserved_seats))
            ['A1', 'A2']
            >>> plane.book_seats("A1", 1)  # Already reserved
            False
            >>> plane.book_seats("A3", 3)  # Beyond seat limit
            False
            >>> plane.book_seats("C1", 1)  # Invalid row
            False
        """
        self.log(f'book_seats start_seat_name={start_seat_name} num_seats={num_seats}')

        # Check if consecutive seats are available from the start_seat_name and for num_seats
        if not self.check_consecutive_seats(start_seat_name, num_seats):
            self.log('Not enough consecutive seats!')
            return False
        
        start_row_idx = ord(start_seat_name[0]) - ord('A')
        start_pos_idx = int(start_seat_name[1:]) # - 1   # Substract 1 to convert from 1-based to 0-based
        
        # Book all the seats
        for i in range(num_seats):
            seat_name = self.get_seat_name(start_row_idx, start_pos_idx + i)
            self.log(f'Reserving seat: {seat_name}')
            self.reserved_seats.add(seat_name)
        
        return True
    
    def cancel_seats(self, start_seat_name, num_seats=1):
        """
        Cancel reservations for multiple consecutive seats.
        Args:
            start_seat_name (str): The first seat in the sequence to be canceled.
            num_seats (int): The number of consecutive seats to cancel.
        Returns:
            bool: True if all specified seats were successfully canceled, False if any seat was not reserved.
    
        Example:
            >>> plane = Airplane("TA101", 2, "xx_xxxx_xx")
            >>> plane.book_seats("A1", 3)
            True
            >>> plane.cancel_seats("A1", 3)
            True
            >>> plane.cancel_seats("A1", 3)  # Already unreserved
            False
        """
        self.log(f'cancel_seats start_seat_name={start_seat_name} num_seats={num_seats}')
    
        if len(start_seat_name) < 2:
            return False

        start_row_idx = ord(start_seat_name[0]) - ord('A')
    
        try:
            start_pos_idx = int(start_seat_name[1:])  # Convert seat number to integer
        except ValueError:
            return False

        # Check if all requested seats are in the same row and within bounds
        if start_row_idx < 0 or start_row_idx >= self.row_count or start_pos_idx < 0 or start_pos_idx + num_seats > self.seats_per_row:
            return False

        for i in range(num_seats):
            seat_name = self.get_seat_name(start_row_idx, start_pos_idx + i)
            if seat_name in self.reserved_seats:
                self.reserved_seats.remove(seat_name)   # Cancel seats that have previously been reserved
            else:
                return False  # At least one seat was not reserved

        return True

    def to_dict(self):
        """
        Convert airplane data to a dictionary for serialization.
        Returns:
            dict: Dictionary representation of the airplane
            
        Example:
            >>> plane = Airplane("TA101", 2, "xx_xxxx_xx")
            >>> plane.reserved_seats.add("A1")
            >>> data = plane.to_dict()
            >>> data["name"]
            'TA101'
            >>> data["row_count"]
            2
            >>> data["row_layout"]
            'xx_xxxx_xx'
            >>> sorted(data["reserved_seats"])
            ['A1']
        """
        self.log(f'to_dict')
        return {
            "name": self.name,
            "row_count": self.row_count,
            "row_layout": self.row_layout,
            "reserved_seats": list(self.reserved_seats)
        }
        
    @classmethod
    def from_dict(cls, data):
        """
        Create an Airplane instance from a dictionary.
        Args:
            data (dict): Dictionary containing airplane data    
        Returns:
            Airplane: New airplane instance
            
        Example:
            >>> data = {"name": "TA101", "row_count": 20, "row_layout": "xx_xxxx_xx", "reserved_seats": ["B1", "C2"]}
            >>> plane = Airplane.from_dict(data)
            >>> plane.name
            'TA101'
            >>> plane.row_count
            20
            >>> sorted(list(plane.reserved_seats))
            ['B1', 'C2']
        """
        # self.log(f'from_dict cls={cls} data={data}')   # classmethod => self is not defined!
        airplane = cls(data["name"], data["row_count"], data["row_layout"])
        airplane.reserved_seats = set(data["reserved_seats"])
        return airplane
    
    def log(self, message):
        """Prints debug messages if debugging is enabled."""
        if self.debug:
            print(f"[DEBUG] [PLANE] {message}", file=sys.stderr)

# %% doctest
if __name__ == "__main__":
    import doctest
    doctest.testmod()
# %%
