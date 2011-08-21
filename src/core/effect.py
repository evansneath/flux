#!/usr/bin/python2.7

"""effect.py

This module contains and organizes the Flux effects.
"""

# Library imports
import logging

class Effect(object):
    """Effect class

    An effect object stores all details relating to a
    single board effect. This includes its name, list
    of effect traits, and whether it is active or
    not. This allows for easy access to effects data

    Attributes:
        name: The string formatted name of the effect.
        is_active: Whether the effect is turned on or off.
        trait_list: A list of effect traits.
    """
    def __init__(self, name, is_active=False):
        """Initialization function for a new effect object

        Arguments:
            name: The name to give the effect.
            is_active: Whether the effect is active from initialization.
        """
        self.__name = name
        self.__is_active = is_active
        self.__trait_list = []

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

    def __get_trait_list(self):
        """Getter for the effect list of traits"""
        return self.__traits

    # Property declarations
    name = property(fget=__get_name, fset=__set_name,
                    doc='Gets or sets the effect name')
    is_active = property(fget=__get_is_active, fset=__set_is_active,
                         doc='Gets or sets the active state of the effect')
    trait_list = property(fget=__get_trait_list, 
                          doc='Gets the list of traits')

    # Public functions
    def toggle(self):
        """Toggles the effect on or off depending on current state"""
        self.__is_active = not self.__is_active

    def add_trait(self, name):
        """Adds a new trait object to the effect's trait list"""
        try:
            self.trait_list.append(Trait(self.__name, name))
            logging.debug('Added new trait ''{0}'' to '
                          'effect ''{1}'''.format(name, self.__name))
            return True
        except:
            logging.debug('Cannot add trait ''{0}'' '
                          'to effect ''{1}'''.format(name, self.__name))
            return False

    def remove_trait_by_name(self, name):
        """Removes an existing trait object from the 
           effect's trait list

        Arguments:
            name: The name of the trait to remove.
        Returns:
            True on success. False if otherwise.
        """
        try:
            self.__trait_list.remove(find_trait(name))
            logging.debug('Removed trait ''{0}'' from '
                          'effect ''{1}'''.format(name, self._name))
            return True
        except:
            logging.debug('Cannot remove trait ''{0}''. Not found '
                          'in effect ''{1}'''.format(name, self.__name))
            return False

    def find_trait_by_name(self, name):
        """Search for a trait by name

        Arguments:
            name: The name of the trait to search for.
        Returns:
            The first trait found by the given name. None if not found.
        """
        found = None
        for trait in self.__trait_list:
            if trait.name == name:
                found = trait
                break
        return found

class EffectLibrary(object):
    """EffectLibrary class

    Contains and manages the list of effects.

    Attributes:
        effect_list: A list of all effects.
    """
    def __init__(self):
        """Initialize effect library object"""
        self.__effect_list = []

    def __get_effect_list(self):
        """Getter for the effect library list of effects"""
        return self.__effects

    effect_list = property(fget=__get_effect_list,
                       doc='Gets the list of effects')

    def add_effect(self, name, is_active=False):
        """Adds a new effect object to the effect library.

        Arguments:
            name: A name to give to the new effect. (default: None)
            is_active: Determines whether the effect is automatically
                       enabled or not. (default: False)
        Returns:
            True on success. False if otherwise.
        """
        try:
            self.__effect_list.append(Effect(name, is_active))
            logging.debug('Added new effect ''{0}'' to library'.format(name))
            return True
        except:
            logging.debug('Cannot add effect ''{0}'' to library'.format(name))
            return False

    def remove_effect_by_name(self, name):
        """Removes an existing effect object from the effect library.

        Arguments:
            name: The name of the effect to remove.
        Returns:
            True on success. False if otherwise.
        """
        try:
            self.__effect_list.remove(find_effect(name))
            logging.debug('Removed effect ''{0}'' from '
                          'library'.format(name))
            return True
        except:
            logging.debug('Cannot remove effect ''{0}''. Not found '
                          'in library'.format(name))
            return False

    def find_effect_by_name(self, name):
        """Search for an effect by name.

        Arguments:
            name: The name of the effect to search for.
        Returns:
            The first effect found by the given name. None if not found.
        """
        found = None
        for effect in self.__effect_list:
            if effect.name == name:
                found = effect
                break
        return found

    def display_tree(self):
        """Prints the full effects tree heirarchy in a
           very simply manner."""
        print('-- library object heirarchy --')
        if not self.__effect_list:
            print('<Empty>')
        for effect in self.__effect_list:
            print('<Effect {0}> - Name:{1}'.format(
                  self.__effect_list.index(effect), effect.name))
            for trait in effect.trait_list:
                 print('\t<Trait {0}> - Name:{1}'.format(
                       effect.trait_list.index(trait), trait.name))

# Main function for class file 
# (should remain relatively unused outside of small-scale class testing)
def main():
    print('hello, effect')
    return

if __name__ == '__main__':
    main()