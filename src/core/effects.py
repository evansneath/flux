#!/usr/bin/python2.7

"""effects.py
    These are the Flux effects classes designed to communicate
    via serial chatter between the warp and stomp modules. This
    does so through the pySerial library. The effects heirarchy
    and their traits are also organized in this class.
"""

# Library imports
import logging

class Trait(object):
    """Trait class

    A trait object stores a single character trait relating
    to a parent effect. This trait has a name as well
    as a trait modifying control located on the Stomp system.

    Attributes:
        parent: The trait's parent effect
        name: The string formatted name of the trait
        control: The controlling hardware input
    """

    # Initialization function
    def __init__(self, parent, name, control):
        """Initialization function for a new trait object.

        Arguments:
            parent: The trait's parent effect.
            name: The name of the trait.
            control: The device on the hardware to control.
        """

        self.__parent = parent
        self.__name = name
        self.__control = control

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

    def __get_control(self):
        """Getter for the trait control"""
        return self.__control

    def __set_control(self, new_control):
        """Setter for the trait control"""
        self.__control = new_control

    # Property declarations
    parent = property(fget=__get_parent, 
                      doc='Gets the parent effect name')
    name = property(fget=__get_name, fset=__set_name,
                    doc='Gets or sets the trait name')
    control = property(fget=__get_control, fset=__set_control,
                       doc='Gets or sets the active trait control')

class Effect(object):
    """Effect class

    An effect object stores all details relating to a
    single board effect. This includes its name, list
    of effect traits, and whether it is active or
    not. This allows for easy access to effects data

    Attributes:
        name: The string formatted name of the effect.
        is_active: Whether the effect is turned on or off.
        traits: A list of effect traits.
    """

    # Initialization function
    def __init__(self, name, is_active=False):
        """Initialization function for a new effect object

        Arguments:
            name: The name to give the effect.
            is_active: Whether the effect is active from initialization.
        """
        self.__name = name
        self.__is_active = is_active
        self.__traits = []

    # Private functions
    def __get_name(self):
        """Getter for the effect name property"""
        return self.__name

    def __set_name(self, new_name):
        """Setter for the effect name property"""
        self.__name = new_name

    def __get_is_active(self):
        """Getter for the effect is_active property"""
        return self.__is_active

    def __set_is_active(self, new_is_active):
        """Setter for the effect is_active property"""
        self.__is_active = new_is_active

    def __get_traits(self):
        """Getter for the effect list of traits"""
        return self.__traits

    # Property declarations
    name = property(fget=__get_name, fset=__set_name,
                    doc='Gets or sets the effect name')
    is_active = property(fget=__get_is_active, fset=__set_is_active,
                         doc='Gets or sets the active state of the effect')
    traits = property(fget=__get_traits, 
                          doc='Gets the list of traits')

    # Public functions
    def toggle(self):
        """Toggles the effect on or off depending on current state"""
        self.__is_active = not self.__is_active

    def add_trait(self, name, control, value=0):
        """Adds a new trait object to the effect's trait list"""
        try:
            self.traits.append(Trait(self.__name, name, control))
            logging.debug('Added new trait ''{0}'' to '
                          'effect ''{1}'''.format(name, self.__name))
            return True
        except:
            logging.debug('Cannot add trait ''{0}'' '
                          'to effect ''{1}'''.format(name, self.__name))
            return False

    def remove_trait(self, name):
        """Removes an existing trait object from the 
           effect's trait list

        Arguments:
            name: The name of the trait to remove.
        Returns:
            True on success. False if otherwise.
        """
        try:
            self.__traits.remove(find_trait(name))
            logging.debug('Removed trait ''{0}'' from '
                          'effect ''{1}'''.format(name, self._name))
            return True
        except:
            logging.debug('Cannot remove trait ''{0}''. Not found '
                          'in effect ''{1}'''.format(name, self.__name))
            return False

    def find_trait(self, name):
        """Search for a trait by name

        Arguments:
            name: The name of the trait to search for.
        Returns:
            The first trait found by the given name. None if not found.
        """
        found = None
        for trait in self.__traits:
            if trait.name == name:
                found = trait
                break
        return found

class Core(object):
    """Core class

    A core object's main priority to to contain the
    list of effects.

    Attributes:
        effect_list: A list of Flux effects.
    """

    # Initialization function
    def __init__(self):
        """Begin core object definition"""
        self.__effects = []

    # Private functions
    def __get_effects(self):
        """Getter for the core list of effects"""
        return self.__effects

    # Property declarations
    effects = property(fget=__get_effects, 
                       doc='Gets the list of effects')

    # Public functions
    def add_effect(self, name, is_active=False):
        """Adds a new effect object to the core.

        Arguments:
            name: A name to give to the new effect. (default: None)
            is_active: Determines whether the effect is automatically
                       enabled or not. (default: False)
        Returns:
            True on success. False if otherwise.
        """
        try:
            self.__effects.append(Effect(name, is_active))
            logging.debug('Added new effect ''{0}'' to core'.format(name))
            return True
        except:
            logging.debug('Cannot add effect ''{0}'' to core'.format(name))
            return False

    def remove_effect(self, name):
        """Removes an existing effect object from the Core.

        Arguments:
            name: The name of the effect to remove.
        Returns:
            True on success. False if otherwise.
        """
        try:
            self.__effects.remove(find_effect(name))
            logging.debug('Removed effect ''{0}'' from '
                          'core'.format(name))
            return True
        except:
            logging.debug('Cannot remove effect ''{0}''. Not found '
                          'in core'.format(name))
            return False

    def find_effect(self, name):
        """Search for an effect by name.

        Arguments:
            name: The name of the effect to search for.
        Returns:
            The first effect found by the given name. None if not found.
        """
        found = None
        for effect in self.__effects:
            if effect.name == name:
                found = effect
                break
        return found

    def print_effect_tree(self):
        """Prints the full effects tree heirarchy in a
           very simply manner."""
        print('-- Core object heirarchy --')
        if not self.__effects:
            print('<Empty>')
        for effect in self.__effects:
            print('<Effect {0}> - Name:{1}'.format(
                  self.__effects.index(effect), effect.name))
            for trait in effect.traits:
                 print('\t<Trait {0}> - Name:{1}'.format(
                       effect.traits.index(trait), trait.name))

# Main function for class file 
# (should remain relatively unused outside of small-scale class testing)
def main():
    print('hello, effects')
    return

if __name__ == '__main__':
    main()