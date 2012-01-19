"""Collection of audio effects that process data contained in QByteArrays"""

import struct
import math
import numpy as np

from PySide import QtCore, QtGui, QtMultimedia

SAMPLE_MAX = 32767
SAMPLE_MIN = -(SAMPLE_MAX + 1)

class Parameter(QtCore.QObject):
    """A description of an effect parameter.
    
    Members:
        maximum -- The largest value that the parameter should contain.
        minumum -- The smallest value that the parameter should contain.
        value   -- The current value of the parameter. It is updated whenever the interface element changes.
        type    -- The type that value sould be stored as.
    """
    def __init__(self, type=int, minimum=0, maximum=100, value=10):
        super(Parameter, self).__init__()
        
        #type must be a callable that will convert a value from a float to the desired type
        self.type = type
        self.minimum = minimum
        self.maximum = maximum
        self.value = value

class AudioEffect(QtCore.QObject):
    """Base class for audio effects."""
    name = 'Unknown Effect'
    description = ''
    
    """A dictionary of str(param_name):Parameter items that describes all parameters that a user can alter."""
    parameters = {}
    
    def process_data(self, data):
        """Modify a np.aray and return the modified array.
        
        This is an abstract method to represent data processing. Override this
        function when subclassing AudioEffect.
        """
        pass

class Decimation(AudioEffect):
    """Decimation / Bitcrushing effect.
        
    Parameters:
        bits -- Amount of bit accuracy in the output data.
        rate -- Sample rate of the output data.
    """
    name = 'Decimation'
    description = 'Reduce signal sample rate and/or bit accuracy'
    parameters = {'Bits':Parameter(int, 8, 16, 16),
                  'Rate':Parameter(float, 0.0, 1.0, 1.0)}
    
    def __init__(self, bits=16, rate=1.0):
        
        super(Decimation, self).__init__()
        
        self.bits = bits
        self.rate = rate
        self.shifted_bits = 1 << (bits - 1)
        self.count = 0
    
    def process_data(self, data):
        for i in xrange(0, len(data), 2):
            value = struct.unpack('<h', data[i:i+2])[0]
            modified_value = 0
            
            self.count += self.rate
            if self.count >= 1:
                self.count -= 1
                modified_value = value * self.shifted_bits / self.shifted_bits
            
            data.replace(i, 2, struct.pack('<h', modified_value))

class FoldbackDistortion(AudioEffect):
    """Foldback distortion
    Parameters:
        threshold -- A factor from 0 to SAMPLE_MAX representing the 
                     maximum allowed value before the signal is clipped.
    """
    name = 'Foldback Distortion'
    description = ''
    parameters = {'Threshold':Parameter(int, 100, SAMPLE_MAX, SAMPLE_MAX)}
    
    def process_data(self, data):
        threshold=self.parameters['Threshold'].value
        def func(value, threshold=threshold):
            return int(math.fabs(math.fabs(math.fmod(
                    value - threshold, threshold * 4)) -
                    threshold * 2) - threshold)
        vec = np.vectorize(func)
        return np.piecewise(data, [data < -threshold, data > threshold], [vec, vec, lambda x: x])

class Gain(AudioEffect):
    """Gain effect
    
    Parameters:
       amount -- A factor by which to multiply the input signal. Unintended
                 clipping can occur if multiplied values exceed 16-bit integer
                 maximum. 
    """
    name = 'Gain'
    description = 'Increase the volume, clipping loud signals'
    parameters = {'Amount':Parameter(float, 0, 10, 1)}
    
    def process_data(self, data):
        return np.multiply(data, self.parameters['Amount'].value)

class Passthrough(AudioEffect):
    """An effect for testing"""
    
    name = 'Passthrough'
    description = 'Does not modify the signal'
    parameters = {'Param 1':Parameter(float, 0, 10, 5),
                  'Param 2':Parameter()}
    

#this tuple needs to be maintained manually
available_effects = (Decimation, FoldbackDistortion, Gain, Passthrough)