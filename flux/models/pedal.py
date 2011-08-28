#!/usr/bin/env python

"""pedal.py

This module defines the Pedal class.
"""

# Library imports
import logging

class Pedal(object):
    """Pedal class

    An effect object stores all details relating to a
    single pedal. This includes its name, list
    of pedal effects, and whether it is active or
    not.

    Attributes:
        name: The string formatted name of the pedal.
        effects: A list of the pedal effects.
    """
    def __init__(self, name):
        """Initialization function for a new pedal object.

        Arguments:
            name: The name to give the pedal.
        """
        super(Pedal, self).__init__()
        self.__name = name
        self.__effect_list = []

    # Private functions
    def __get_name(self):
        """Getter for the pedal name property."""
        return self.__name

    def __set_name(self, new_name):
        """Setter for the pedal name property."""
        self.__name = new_name

    def __get_effects(self):
        """Getter for the pedal list of effects."""
        return self.__effects

    # Property declarations
    name = property(fget=__get_name, fset=__set_name,
                    doc='Gets or sets the pedal name.')
    effects = property(fget=__get_effects, 
                          doc='Gets the list of effects.')
    
    def stack(self, effect):
        pass
    
    def unstack(self):
        pass
    
    def synthesize(self):
        pass
    
    def start(self):
        pass
    
    def stop(self):
        pass

# Main function for class file 
# (should remain relatively unused outside of small-scale class testing)
def main():
    print('hello, pedal')
    return

if __name__ == '__main__':
    main()