"""Collection of audio effects that process data contained in QByteArrays"""

import struct
import math

from PySide import QtCore, QtGui, QtMultimedia

SAMPLE_MAX = 32767
SAMPLE_MIN = -SAMPLE_MAX

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
<<<<<<< HEAD
        """Apply effect processing to data, modifying data in place."""
        pass
    
    @classmethod
    def pack_short(cls, value):
        """Pack a python int into a short int byte string"""
        #truncate value to a signed short int
        if value < SAMPLE_MIN:
            value = SAMPLE_MIN
        elif value > SAMPLE_MAX:
            value = SAMPLE_MAX
        return struct.pack('<h', value)
=======
        """Abstract data processing method.
        
        This is an abstract method to represent data processing. Override this
        function upon new AudioEffect object creation.
        
        Args:
            data: A chunk of input data to process.
        
        Returns:
            Processed data for further processing by another effect or output.
        """
        pass

class Decimation(AudioEffect):
    def __init__(self, bits=16, rate=1.0):
        """Decimation effect initiation.
        
        Args:
            bits: Amount of bit accuracy in the output data.
            rate: Sample rate of the output data.
        """
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
    def __init__(self, threshold=1.0):
        """Foldback distortion effect initialization.
        
        Args:
            threshold: A factor from 0.0 to 1.0 representing the percentage of
                maximum allowed value to clip.
        """
        super(FoldbackDistortion, self).__init__()
>>>>>>> Added Decimation(BitCrush) effect and comments
        
class FoldbackDistortion(AudioEffect):
    name = 'Foldback Distortion'
    description = ''
    parameters = {'Threshold':Parameter(int, 1, SAMPLE_MAX, SAMPLE_MAX)}
    
    def process_data(self, data):
        modified_data = QtCore.QByteArray()
        modified_data.reserve(data.size())
        threshold = self.parameters['Threshold'].value
        for i in xrange(0, len(data), 2):
            value = struct.unpack('<h', data[i:i+2])[0]
            if value > threshold or value < -threshold:
                value = math.floor(math.fabs(math.fabs(math.fmod(
                        value - threshold, threshold * 4)) -
                        threshold * 2) - threshold)
            
            modified_data.append(self.pack_short(value))
            
        data.setRawData(str(modified_data), modified_data.size())

class Gain(AudioEffect):
<<<<<<< HEAD
    name = 'Gain'
    description = 'Increase the volume, clipping loud signals'
    parameters = {'Amount':Parameter(float, 0, 10, 1)}
=======
    def __init__(self, amount=2):
        """Gain effect initialization.
        
        Args:
            amount: A factor by which to multiply the input signal. Unintended
                clipping can occur if multiplied values exceed 16-bit integer
                maximum.
        """
        super(Gain, self).__init__()
        
        self.amount = amount
>>>>>>> Added Decimation(BitCrush) effect and comments
    
    def process_data(self, data):
        modified_data = QtCore.QByteArray()
        modified_data.reserve(data.size())
        
        for i in xrange(0, len(data), 2):
            value = struct.unpack('<h', data[i:i+2])[0] * self.parameters['Amount'].value
            modified_data.append(self.pack_short(value))
            
        data.setRawData(str(modified_data), modified_data.size())

class Passthrough(AudioEffect):
    """An effect for testing"""
    
    name = 'Passthrough'
    description = 'Does not modify the signal'
    
    parameters = {'Param 1':Parameter(float, 0, 10, 5),
                  'Param 2':Parameter()}
    

#this tuple needs to be maintained manually
available_effects = (FoldbackDistortion, Gain, Passthrough)
