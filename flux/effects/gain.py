import numpy as np

from _base import *

class Gain(AudioEffect):
    """Gain effect
    
    Parameters:
       amount -- A factor by which to multiply the input signal. Unintended
                 clipping can occur if multiplied values exceed 16-bit integer
                 maximum. 
    """
    name = 'Gain'
    description = 'Increase the volume, clipping loud signals'
    
    def __init__(self):
        super(Gain, self).__init__()
        self.parameters = {'Amount':Parameter(float, 0, 20, 1)}
    
    def process_data(self, data):
        return np.multiply(data, self.parameters['Amount'].value)
