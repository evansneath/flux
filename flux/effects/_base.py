import collections

from PySide import QtCore

__all__ = ['SAMPLE_SIZE', 'SAMPLE_RATE', 'SAMPLE_MAX', 'NYQUIST', 'SAMPLE_MIN', 'CHANNEL_COUNT', 'BUFFER_SIZE',
           'AudioEffect', 'Parameter', 'TempoParameter', 'DiscreteParameter'] 

SAMPLE_MAX = 32767
SAMPLE_MIN = -(SAMPLE_MAX + 1)
SAMPLE_RATE = 44100. # [Hz]
NYQUIST = SAMPLE_RATE / 2
SAMPLE_SIZE = 16 # [bit]
CHANNEL_COUNT = 1
BUFFER_SIZE = 2500 #this is the smallest buffer that prevents underruns on my machine


class AudioEffect(QtCore.QObject):
    """Base class for audio effects."""
    name = 'Unknown Effect'
    description = ''
    
    def __init__(self):
        """parameters -- A dictionary of str(param_name):Parameter items that describes all parameters that a user can alter."""
        super(AudioEffect, self).__init__()
        self.parameters = {}
    
    def process_data(self, data):
        """Modify a numpy.array and return the modified array.
        
        This is an abstract method to represent data processing. Override this
        function when subclassing AudioEffect.
        """
        return data

class Parameter(QtCore.QObject):
    """A description of an effect parameter.
    
    Members:
        maximum  -- The largest value that the parameter should contain.
        minumum  -- The smallest value that the parameter should contain.
        value    -- The current value of the parameter. It is updated whenever the interface element changes.
        type     -- The type that value sould be stored as.
        inverted -- If True, a slider at the highest position will produce the minimum value and vice versa.
    """
    
    #Signal emited when value member changes
    value_changed = QtCore.Signal()
    
    def __init__(self, type=int, minimum=0, maximum=100, value=10, inverted=False):
        super(Parameter, self).__init__()
        
        #type must be a callable that will convert a value from a float to the desired type
        self.type = type
        self.minimum = minimum
        self.maximum = maximum
        self._value = value
        self.inverted = inverted
        
    def __repr__(self):
        return '%s(%s, %s, %s, %s, %i)' % (self.__class__.__name__, self.type, self.minimum, self.maximum, self.value, self.inverted)
        
    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, val):
        self._value = val
        self.value_changed.emit()
        

class TempoParameter(Parameter):
    """A Parameter whose value can be overridden by a user supplied tempo, in beats-per-minute.
    
    If use_bpm is True, value will be an integer with 0 < value < 1000.
    Otherwise value will be a value adhering to minumum, maximum and type, as usual.
    """
    bpm = 0
    
    def __init__(self, type=int, minimum=0, maximum=100, value=10):
        super(TempoParameter, self).__init__(type, minimum, maximum, value)
        
        self._value = value
        self.use_bpm = False
    
    @property
    def value(self):
        if self.use_bpm:
            return self.bpm
        return self._value
    
    @value.setter
    def value(self, val):
        self._value = val
        self.value_changed.emit()

    @classmethod
    def set_bpm(cls, value):
        cls.bpm = value
        
    def set_use_bpm(self, value):
        self.use_bpm = value

class DiscreteParameter(Parameter):
    """A Parameter with a set of discrete values instead of a range.
    
    Members:
        choices_dict -- a dictionary mapping names of available choices to their
                        optional icon file path if no icon is desired, the path
                        should be an empty string
        value        -- the name currently selected choice
    """

    def __init__(self, choices_dict, value):
        super(DiscreteParameter, self).__init__()
        self.choices_dict = collections.OrderedDict(choices_dict)
        self._value = value