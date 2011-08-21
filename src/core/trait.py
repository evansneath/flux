
"""trait.py

This module contains and organizes trait objects
"""

# Library imports
import sndobj

class Trait(object):
    """Trait class

    A trait object stores a single character trait relating
    to a parent effect.

    Attributes:
        parent: The trait's parent effect
        name: The string formatted name of the trait
    """

    # Initialization function
    def __init__(self, parent, name):
        """Initialization function for a new trait object.

        Arguments:
            parent: The trait's parent effect.
            name: The name of the trait.
        """
        self.__parent = parent
        self.__name = name

    # Private functions
    def __get_parent(self):
        """Getter for the trait parent. Parent value may
           not be changed as this trait is owned completely"""
        return self.__parent

    def __get_name(self):
        """Getter for the trait name"""
        return self.__name

    def __set_name(self, new_name):
        """Setter for the trait name"""
        self.__name = new_name

    # Property declarations
    parent = property(fget=__get_parent, 
                      doc='Gets the parent effect name')
    name = property(fget=__get_name, fset=__set_name,
                    doc='Gets or sets the trait name')

class Gain(Trait):
    """Gain class
    
    Representing an effect gain of the output signal.
    
    Attributes:
        parent: The gain trait's parent effect.
        name: The string formatted name of the gain trait.
        level: The active level of the gain. [dB]
        multiplier: The multiplication factor of the gain. [-]
    """
    def __init__(self, parent, name, level=10, multiplier=1):
        """Initialization function for a new Gain object.
        
        Arguments:
            parent: The gain's parent effect.
            name: The string formatted name of the gain trait.
            level: The active level of the gain. [dB]
            multiplier: The multiplication factor of the gain. [-]
        """
        super(StaticGain, self).__init__(parent, name)
        self.__level = level
        self.__multiplier = multiplier
        self.__gain = sndobj.Gain()
        self.__gain.SetGain(level)
        self.__gain.SetGainM(multiplier)

    def __get_level(self):
        """Getter for the gain level property [dB]"""
        return self.__level
    
    def __set_level(self, new_level):
        """Setter for the gain level property [dB]"""
        self.__level = new_level
        self.__gain.SetGain(new_level)

    def __get_multiplier(self):
        """Getter for the gain multiplier property [-]"""
        return self.__multiplier
    
    def __set_multiplier(self, new_multiplier):
        """Setter for the gain multiplier property [-]"""
        self.__multiplier = new_multiplier
        self.__gain.SetGainM(new_multiplier)

    level = property(fget=__get_level, fset=__set_level,
                     doc='Gets or sets the gain level [dB]')
    multiplier = property(fget=__get_multiplier, fset=__set_multiplier,
                          doc='Gets or sets the gain multiplier [-]')

class Phase(Trait):
    """Phase class
    
    Represents an effect phase augmentation.
    
    Attributes:
        parent: The gain's parent effect.
        name: The string formatted name of the gain trait.
        frequency: The phasor frequency. [Hz]
        offset: Signal phase in fractions of a cycle. [-] (0 to 1.0)
    """
    def __init__(self, parent, name, frequency=0, offset=0):
        """Initializes the phase trait.
        
        Arguments:
            parent: The gain's parent effect.
            name: The string formatted name of the gain trait.
            frequency: The phasor frequency. [Hz]
            offset: Initial phase offset in fractions of a cycle. [-] (0 to 1.0)
        """
        super(Phase, self).__init__(parent, name)
        self.__frequency = frequency
        self.__offset = offset
        self.__phase = sndobj.Phase()
        self.__phase.SetFreq(frequency)
        self.__phase.SetPhase(offset)

    def __get_frequency(self):
        """Getter for the phasor frequency property"""
        return self.__frequency
    
    def __set_frequency(self, new_frequency):
        """Setter for the phasor frequency property"""
        self.__frequency = new_frequency
        self.__phase.SetFreq(new_frequency)

    def __get_offset(self):
        """Getter for the phase offset property"""
        return self.__offset

    def __set_offset(self, new_offset):
        """Setter for the phase offset property"""
        self.__offset = new_offset
        self.__phase.SetPhase(new_offset)

    frequency = property(fget=__get_frequency, fset=__set_frequency,
                         doc='Gets or sets the phase frequency [Hz]')
    offset = property(fget=__get_offset, fset=__set_offset,
                      doc='Gets or sets the phase offset [-]')

# Main function for class file
# (should remain relatively unused outside of small-scale class testing)
def main():
    print('hello, trait')
    return

if __name__ == '__main__':
    main()