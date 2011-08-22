#!/usr/bin/python2.7

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
        identifier: The control's byte message identifier.
    """
    def __init__(self, name, identifier):
        """Initialization function for a new control object
        
        Arguments:
            name: The readable name of the control.
            identifier: The control's byte message identifier.
        """
        self.__name = name
        self.__identifier = identifier
    
    def __get_name(self):
        """Getter for the control name"""
        return self.__name

    def __set_name(self, new_name):
        """Setter for the control name"""
        self.__name = new_name
    
    def __get_identifier(self):
        """Getter for the control identifier"""
        return self.__identifier
    
    def __set_identifier(self, new_identifier):
        """Setter for the control identifier"""
        self.__identifier = new_identifier

    name = property(fget=__get_name, fset=__set_name,
                    doc='Gets or sets the control name')
    identifier = property(fget=__get_identifier, fset=__set_identifier,
                          doc='Gets or sets the control identifier')

class SwitchControl(Control):
    """SwitchControl class
    
    A subclass of control used to represent a switch control.
    
    Attributes:
        is_active: Determines whether the switch is on or off.
    """
    def __get_is_active(self):
        """Getter for the switch's current state"""
        return self.__is_active
    
    def __set_is_active(self, new_is_active):
        """Setter for the switch's current state"""
        self.__is_active = new_is_active
    
    is_active = property(fget=__get_is_active, fset=__set_is_active,
                         doc='Gets or sets the switch current active state')

class DialControl(Control):
    """DialControl class
    
    A subclass of control used to represent a dial control.
    
    Attributes:
        percent: The percentage value of the dial (0=min, 100=max)
    """
    def __get_percent(self):
        """Getter for the dial's current percentage value"""
        return self.__percent
    
    def __set_percent(self, new_percent):
        """Setter for the dial's current percentage value"""
        self.__percent = new_percent
    
    percent = property(fget=__get_percent, fset=__set_percent,
                       doc='Gets or sets the dial current percentage')

class WahControl(DialControl):
    """WahControl class
    
    A subclass of dial control used to represent a wah pedal control.
    """
    pass

# Main function for class file
# (should remain relatively unused outside of small-scale class testing)
def main():
    print('hello, control')
    return

if __name__ == '__main__':
    main()