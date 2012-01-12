"""Collection of audio effects that process data contained in QByteArrays"""

import struct
import math

#Use PyQt API 2
import sip
sip.setapi('QString', 2)
from PyQt4 import QtCore, QtGui, QtMultimedia

class AudioEffect(QtCore.QObject):
    def process_data(self, data):
        #Override this method to process data before writing to output.
        pass

class FoldbackDistortion(AudioEffect):
    def __init__(self, threshold=1.0):
        super(FoldbackDistortion, self).__init__()
        
        self.threshold = threshold * 32767
    
    def process_data(self, data):        
        for i in xrange(0, len(data), 2):
            value = struct.unpack('<h', data[i:i+2])[0]
            
            if value > self.threshold or value < -self.threshold:
                value = math.floor(math.fabs(math.fabs(math.fmod(
                    value - self.threshold, self.threshold * 4)) -
                    self.threshold * 2) - self.threshold)
            
            data.replace(i, 2, struct.pack('<h', value))

class Gain(AudioEffect):
    def __init__(self, amount=2):
        super(Gain, self).__init__()
        
        self.amount = amount
    
    def process_data(self, data):
        for i in xrange(0, len(data), 2):
            value = struct.unpack('<h', data[i:i+2])[0] * self.amount
            #Hard clip value to a signed short int
            if value < -32768:
                value = -32768
            elif value > 32767:
                value = 32767
            #modify the data in place 
            data.replace(i, 2, struct.pack('<h', value))