import struct

#Use PyQt API 2
import sip
sip.setapi('QString', 2)
from PyQt4 import QtCore, QtGui, QtMultimedia

class AudioEffect(QtCore.QObject):
    def processData(self, data):
        #Override this method to process data before writing to output.
        pass
    
class Gain(AudioEffect):
    def __init__(self, amount=2):
        super(Gain, self).__init__()
        
        self.amount = amount
        
    def processData(self, data):
        for i in xrange(0, len(data), 2):
            value = struct.unpack('<h', data[i:i+2])[0] * self.amount
            #Hard clip value to a signed short int
            if value < -32768:
                value = -32768
            elif value > 32767:
                value = 32767
            #modify the data in place 
            data.replace(i, 2, struct.pack('<h', value))