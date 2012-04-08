"""Effects subpackage that contains AudioEffects.

This file uses some deep magick to import all AudioEffect subclasses found
in submodules into the effects namespace.
"""

import os
import importlib
import sys
import inspect

from PySide import QtCore

import _base
from _base import *

#Note: more names are added to __all__ later.
__all__ =  ['available_effects'] + _base.__all__


#now import all files in the subpackage and their AudioEffect subclasses
available_effects = []

#get the path of the effects package. We cant' use './' because that is the path to the executable 
path = os.path.split(__file__)[0]

for entry in os.listdir(path):
    name, ext = os.path.splitext(entry)
    if not name.startswith('_') and ext.lower() == '.py' and name not in sys.modules:
        #import the module as a module relative to the effects subpackage so that
        #    imports within the module work as expected
        module = importlib.import_module('.' + name, 'effects')
        for name, member in inspect.getmembers(module):
            #only import package members that are subclasses of AudioEffect
            #don't import AudioEffect itself
            if (not name.startswith('_') and inspect.isclass(member) and
                issubclass(member, AudioEffect) and member != AudioEffect):
                available_effects.append(member)
                __all__.append(name)
                
del path
