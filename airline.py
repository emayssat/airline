#%% packages
import os
import sys
import yaml

from airplane import Airplane

#%% constants
DEFAULT_DEBUG=False


#%% airline class definiton
class Airline:
    def __init__(self, name):
        """
        Instanciate the airline company by name
        Args:
            name (str): Name of the airline company
        Example:
            >>> airline = Airline("Test Airways")
            >>> airline.name
            'Test Airways'
            >>> len(airline.airplanes)
            0
            >>> airline.default_snapshot_filename == 'test_airways.snap'
            True
        """
        self.debug = os.environ.get("DEBUG", str(DEFAULT_DEBUG)).lower() in ("1", "true", "yes", "on")
        self.log(f'__init__ name={name}')
        self.name = name
        self.airplanes = {}
        self.default_snapshot_filename = f"{name.lower().replace(' ', '_')}.snap"
        self.default_airplane_name = None

    def add_airplane(self, airplane_name, row_count=20, row_layout="xx_xxxx_xx"):
        """
        Add a new airplane to the fleet.
        Args:
            airplane_name (str): Unique identifier for the airplane
            row_count (int, optional): Number of rows. Defaults to 20.
            row_layout (str, optional): Seat layout pattern. Defaults to "xx_xxxx_xx".
        Returns:
            bool: True if added successfully, False if name already exists

        Example:
            >>> airline = Airline("Test Airways")
            >>> airline.add_airplane("TA101")
            True
            >>> "TA101" in airline.airplanes
            True
            >>> airline.add_airplane("TA101")  # Already exists
            False
            >>> airline.default_airplane_name == 'TA101'
            True
        """
        self.log(f'add_airplane airplane_name={airplane_name} row_count={row_count} row_layout={row_layout}')
        if airplane_name in self.airplanes:
            return False
        
        self.airplanes[airplane_name] = Airplane(airplane_name, row_count, row_layout)

        # If no default airplane name, default to the one that was just added
        if self.default_airplane_name is None:
            self.default_airplane_name = airplane_name

        return True
    
    def delete_airplane(self, airplane_name):
        """
        Delete an airplane from the fleet.
        Args:
            airplane_name (str): Name of the airplane to delete
        Returns:
            bool: True if airplane was deleted, False if it wasn't found
                
        Example:
            >>> airline = Airline("Test Airways")
            >>> airline.add_airplane("TA101")
            True
            >>> airline.add_airplane("TA202")
            True
            >>> "TA101" in airline.airplanes
            True
            >>> airline.delete_airplane("TA101")
            True
            >>> "TA101" in airline.airplanes
            False
            >>> "TA202" in airline.airplanes
            True
            >>> airline.delete_airplane("TA999")  # Non-existent airplane
            False
        """
        self.log(f'delete_airplane airplane_name={airplane_name}')
        if airplane_name in self.airplanes:
            del self.airplanes[airplane_name]
            return True
        return False
    
    def get_airplane(self, airplane_name):
        """
        Get an airplane by name.
        Args:
            airplane_name (str): Name of the airplane to retrieve
        Returns:
            Airplane or None: The airplane object if found, otherwise None
            
        Example:
            >>> airline = Airline("Test Airways")
            >>> airline.add_airplane("TA101", 20)
            True
            >>> plane = airline.get_airplane("TA101")
            >>> plane.row_count
            20
            >>> airline.get_airplane("TA999") is None
            True
        """
        self.log(f'get_airplane airplane_name={airplane_name}')
        return self.airplanes.get(airplane_name)
    
    def get_airplane_names(self):
        """
        Get a list of all airplane names in the fleet.
        Returns:
            list: A list of airplane names (strings)
            
        Example:
            >>> airline = Airline("Test Airways")
            >>> airline.add_airplane("TA101")
            True
            >>> airline.add_airplane("TA202")
            True
            >>> sorted(airline.get_airplane_names())
            ['TA101', 'TA202']
            >>> airline = Airline("Empty Airways")
            >>> airline.get_airplane_names()
            []
        """
        self.log(f'get_airplane_names')
        return list(self.airplanes.keys())

    def to_dict(self):
        """
        Convert airline instance to a dictionary.
        Returns:
            dict: Dictionary representation of the airline instance.

        Example:
            >>> airline = Airline("Test Airways")
            >>> airline.add_airplane("TA101")
            True
            >>> plane = airline.get_airplane("TA101")
            >>> plane.book_seat("A2")
            True
            >>> airline.to_dict()  # Check dictionary structure with seat reservations
            {'name': 'Test Airways', 'airplanes': [{'name': 'TA101', 'row_count': 20, 'row_layout': 'xx_xxxx_xx', 'reserved_seats': ['A2']}]}
        """
        self.log(f'to_dict')
        return {
            "name": self.name,
            "airplanes": [airplane.to_dict() for airplane in self.airplanes.values()]
        }
    
    def load_snapshot(self, snapshot_filename=None):
        """
        Reset airline with its airplane data from a snapshot file.
        Returns:
            bool: True if added successfully, False if name already exists

        Example:
            >>> airline = Airline("Test Airways")
            >>> airline.add_airplane("TA101")
            True
            >>> airline.add_airplane("TA202")
            True
            >>> filename = 'test_load.snap'
            >>> airline.save_snapshot(filename)
            True
            >>> airline.delete_airplane("TA101")
            True
            >>> airline.get_airplane("TA101") is None
            True
            >>> airline.load_snapshot(filename)
            True
            >>> airline.get_airplane("TA101") is not None
            True
            >>> os.path.exists(filename)
            True
            >>> None # or os.remove(filename)
        """
        self.log(f'log_snapshot snapshot_filename={snapshot_filename}')
        if snapshot_filename is None:
            snapshot_filename = self.default_snapshot_filename

        self.log(f'Using snapshot_filename={snapshot_filename}')

        if not os.path.exists(snapshot_filename):
            return False
        else:
            self.log(f'Found snapshot file!')
            try:
                with open(snapshot_filename, 'r') as f:
                    data = yaml.safe_load(f)
                    if data:
                        # Load airplanes in addition to those already loaded
                        for airplane_entry in data.get("airplanes", []):
                            airplane = Airplane.from_dict(airplane_entry)
                            self.airplanes[airplane.name] = airplane
            except Exception as e:
                sys.stderr.write(f"Error loading data: {str(e)}\n")
                return False
            else:
                return True
    
    def save_snapshot(self, snapshot_filename=None):
        """
        Save airline's airplane data in a snapshot file.
        Returns:
            bool: True if completed successfully, False if snapshot filename is invalid

        Example:
            >>> airline = Airline("Test Airways")
            >>> airline.add_airplane("TA101")
            True
            >>> filename = 'test_save.snap'
            >>> airline.save_snapshot(filename)
            True
            >>> os.path.exists(filename)
            True
            >>> None # or os.remove(filename)
        """
        self.log(f'save_snapshot snapshot_filename={snapshot_filename}')
        if snapshot_filename is None:
            snapshot_filename = self.default_snapshot_filename

        # Only allow the creation of *.snap files
        if not snapshot_filename.endswith('.snap'):
            return False

        try:
            with open(snapshot_filename, 'w') as f:
                yaml.dump(self.to_dict(), f, default_flow_style=False, sort_keys=False)
        except Exception as e:
            sys.stderr.write(f"Error saving data: {str(e)}\n")
            return False
        else:
            return True


    def log(self, message):
        """Prints debug messages if debugging is enabled."""
        if self.debug:
            print(f"[DEBUG] [LINE] {message}")


# %% doctesting
if __name__ == "__main__":
    import doctest
    doctest.testmod()

# %%
