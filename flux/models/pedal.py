#!/usr/bin/env python

"""pedal.py

This module defines the Pedal class.
"""

# Library imports
from chain import Chain

class Pedal(Chain):
    """Pedal class

    An effect object stores all details relating to a
    single pedal. This includes its name, list
    of pedal effects, and whether it is active or
    not.

    Attributes:
        name: The name of the pedal.
        description: A descriptive string of the pedal's function.
    """
    def __init__(self, name):
        """Initialization function for a new pedal object.

        Arguments:
            name: The name to give the pedal.
        """
        super(Pedal, self).__init__()
        self.__name = name
        self.__description = None

    # Private functions
    def __get_name(self):
        """Getter for the pedal name property."""
        return self.__name

    def __set_name(self, new_name):
        """Setter for the pedal name property."""
        self.__name = new_name
    
    def __get_description(self):
        """Getter for the pedal description property."""
        return self.__description
    
    def __set_description(self, new_description):
        """Setter for hte pedal description property."""
        self.__description = new_description

    # Property declarations
    name = property(fget=__get_name, fset=__set_name,
                    doc='Gets or sets the pedal name.')
    description = property(fget=__get_description, fset=__set_description,
                           doc='Gets or sets the pedal description.')

def main():
    print('hello, pedal')
    return

if __name__ == '__main__':
    main()