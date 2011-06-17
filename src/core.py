#!/usr/bin/python3.2

"""core.py
    This is the Flux Core class designed to communicate
    via serial chatter between the warp and stomp modules. This
    does so through the pySerial library. The effects heirarchy
    and their properties are also organized in this class.
"""

# Python standard library imports
import logging

#TODO(evan): Implement the Core.effects and Effect.properties lists
#            as dictionaries for a 1:1 name-object lookup time. This
#            will make things much more responsive.


class Property(object):
    """Property class

    A Property object stores a single property relating
    to a parent Effect. This property has a name as well
    as a default property value and a property modifying
    control located on the Stomp system.

    Attributes:
        parent: The property's parent effect
        name: The string formatted name of the property
        control: The controlling hardware input
        value: The value of the property's control
    """

    # Initialization function
    def __init__(self, parent, name, control, value=0):
        """Initialization function for a new Property object

        Arguments:
            parent: The Property's parent class.
            name: The name of the Property.
            control: The device on the hardware to
                     control the Property value.
            value: The value of the Property.
        """

        self.__parent = parent
        self.__name = name
        self.__control = control
        self.__value = value

    # Private functions
    def __get_parent(self):
        """Getter for the Property parent. Parent value may
           not be changed as this property is owned completely"""
        return self.__parent

    def __get_name(self):
        """Getter for the Property name"""
        return self.__name

    def __set_name(self, new_name):
        """Setter for the Property name"""
        self.__name = new_name

    def __get_value(self):
        """Setter for the Property value. Not all properties
           may have their values set (e.g. potentiometer, toggle)"""
        return self.__value

    def __get_control(self):
        """Getter for the Property control"""
        return self.__control

    def __set_control(self, new_control):
        """Setter for the Property control"""
        self.__control = new_control

    # Property declarations
    parent = property(fget=__get_parent, 
                      doc='Gets the parent effect name')
    name = property(fget=__get_name, fset=__set_name,
                    doc='Gets or sets the property name')
    value = property(fget=__get_value, 
                     doc='Gets or sets the property value')
    control = property(fget=__get_control, fset=__set_control,
                       doc='Gets or sets the active property control')


class Effect(object):
    """Effect class

    An Effect object stores all details relating to a
    single board effect. This includes its name, list
    of effect properties, and whether it is active or
    not. This allows for easy access to effects data

    Attributes:
        name: The string formatted name of the effect
        shred: The file name of the effect's ChucK shred
        is_active: Whether the effect is turned ON or OFF
        properties: A list of effect properties
    """

    # Initialization function
    def __init__(self, name, shred, is_active=False):
        """Initialization function for a new Effect object

        Arguments:
            name: The name to give the Effect.
            shred: The shred file name to give the Effect.
            is_active: Whether the Effect is active from initialization.
        """
        self.__name = name
        self.__shred = shred
        self.__is_active = is_active
        self.__properties = []

    # Private functions
    def __get_name(self):
        """Getter for the Effect name property"""
        return self.__name

    def __set_name(self, new_name):
        """Setter for the Effect name property"""
        self.__name = new_name

    def __get_shred(self):
        """Getter for the Effect shred property"""
        return self.__shred

    def __set_shred(self, new_shred):
        """Setter for the Effect shred property"""
        self.__shred = new_shred

    def __get_is_active(self):
        """Getter for the Effect is_active property"""
        return self.__is_active

    def __set_is_active(self, new_is_active):
        """Setter for the Effect is_active property"""
        self.__is_active = new_is_active

    def __get_properties(self):
        """Getter for the Effect list of properties"""
        return self.__properties

    # Property declarations
    name = property(fget=__get_name, fset=__set_name,
                    doc='Gets or sets the effect name')
    shred = property(fget=__get_shred, fset=__set_shred,
                     doc='Gets or sets the associated shred')
    is_active = property(fget=__get_is_active, fset=__set_is_active,
                         doc='Gets or sets the active state of the effect')
    properties = property(fget=__get_properties, 
                          doc='Gets the list of properties')

    # Public functions
    def toggle(self):
        """Toggles the effect ON or OFF depending on current state"""
        self.__is_active = not self.__is_active

    def add_property(self, name, control, value=0):
        """Adds a new Property object to the Effect's property list"""
        try:
            self.properties.append(Property(self.__name, name, control, value))
            logging.debug('Added new property ''{0}'' to '
                          'effect ''{1}'''.format(name, self.__name))
            return True
        except:
            logging.debug('Cannot add property ''{0}'' '
                          'to effect ''{1}'''.format(name, self.__name))
            return False

    def remove_property(self, name):
        """Removes an existing Property object from the 
           Effect's property list

        Arguments:
            name: The name of the property to remove.
        Returns:
            True on success. False if otherwise.
        """
        try:
            self.__properties.remove(find_property(name))
            logging.debug('Removed property ''{0}'' from '
                          'effect ''{1}'''.format(name, self._name))
            return True
        except:
            logging.debug('Cannot remove property ''{0}''. Not found '
                          'in effect ''{1}'''.format(name, self.__name))
            return False

    def find_property(self, name):
        """Search for a property by name

        Arguments:
            name: The name of the property to search for.
        Returns:
            The first property found by the given name. None if not found.
        """
        found = None
        for prop in self.__properties:
            if prop.name == name:
                found = prop
                break
        return found


class Core(object):
    """Core class

    A Core object's main priority to to contain the
    list of effects.

    Attributes:
        effect_list: A list of Flux effects
    """

    # Initialization function
    def __init__(self):
        """Begin core object definition"""
        self.__effects = []

    # Private functions
    def __get_effects(self):
        """Getter for the Core list of effects"""
        return self.__effects

    # Property declarations
    effects = property(fget=__get_effects, 
                       doc='Gets the list of effects')

    # Public functions
    def add_effect(self, name, shred, is_active=False):
        """Adds a new Effect object to the Core.

        Arguments:
            name: A name to give to the new Effect. (default: None)
            shred: A shred file name to give the new Effect. (default: None)
            is_active: Determines whether the Effect is automatically
                       enabled or not. (default: False)
        Returns:
            True on success, False if otherwise.
        """
        try:
            self.__effects.append(Effect(name, shred, is_active))
            logging.debug('Added new effect ''{0}'' to core'.format(name))
            return True
        except:
            logging.debug('Cannot add effect ''{0}'' to core'.format(name))
            return False

    def remove_effect(self, name):
        """Removes an existing Effect object from the Core.

        Arguments:
            name: The name of the effect to remove.
        Returns:
            True on success, False if otherwise.
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
            for prop in effect.properties:
                 print('\t<Property {0}> - Name:{1}'.format(
                       effect.properties.index(prop), prop.name))


# Main function for class file 
# (should remain relatively unused outside of small-scale class testing)
def main():
    print('hello, core')
    return

if __name__ == '__main__':
    main()
