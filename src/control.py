#!/usr/bin/env python

"""control.py

This module contains all of the objects representing the Stomp onboard
controls. This includes toggle switches, wah pedals, dials, etc.
"""

class Control(object):
    """Control class
    
    A control object stores its unique control identifier used to communicate
    to the Stomp subsystem as well as an actively updated value.
    
    Attributes:
        name: The readable name of the control.
        id: The control's byte message identifier.
    """
    def __init__(self, name, id):
        """Initialization function for a new control object.
        
        Arguments:
            name: The readable name of the control.
            id: The control's byte message identifier.
        """
        super(Control, self).__init__()
        self.__name = name
        self.__id = id
    
    def __get_name(self):
        """Getter for the control name."""
        return self.__name

    def __set_name(self, new_name):
        """Setter for the control name."""
        self.__name = new_name
    
    def __get_id(self):
        """Getter for the control identifier."""
        return self.__id
    
    def __set_id(self, new_id):
        """Setter for the control identifier."""
        self.__id = new_id

    name = property(fget=__get_name, fset=__set_name,
                    doc='Gets or sets the control name.')
    identifier = property(fget=__get_id, fset=__set_id,
                          doc='Gets or sets the control identifier.')

class Switch(Control):
    """Switch class
    
    A subclass of control used to represent a switch control.
    
    Attributes:
        name: The readable name of the switch control.
        id: The switch control's byte message identifier.
        is_active: Determines whether the switch control is on or off.
    """
    def __get_is_active(self):
        """Getter for the switch control's current state."""
        return self.__is_active
    
    def __set_is_active(self, new_is_active):
        """Setter for the switch control's current state."""
        self.__is_active = new_is_active
    
    is_active = property(fget=__get_is_active, fset=__set_is_active,
                         doc='Gets or sets the switch current active state.')

class Dial(Control):
    """Dial class
    
    A subclass of control used to represent a dial control.
    
    Attributes:
        name: The readable name of the dial control.
        id: The dial control's byte message identifier.
        percent: The percentage value of the dial. (0=min, 100=max)
    """
    def __get_percent(self):
        """Getter for the dial control's current percentage value."""
        return self.__percent
    
    def __set_percent(self, new_percent):
        """Setter for the dial control's current percentage value."""
        self.__percent = new_percent
    
    percent = property(fget=__get_percent, fset=__set_percent,
                       doc='Gets or sets the dial current percentage')

class Wah(Dial):
    """Wah class
    
    A subclass of dial control used to represent a wah pedal control.
    
    Attributes:
        name: The readable name of the wah control.
        id: The wah control's byte message identifier.
        percent: The percentage value of the wah. (0=min, 100=max)
    """
    pass

# Main function for class file
# (should remain relatively unused outside of small-scale class testing)
def main():
    print('hello, control')
    return

if __name__ == '__main__':
    main()