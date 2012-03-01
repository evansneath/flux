import numpy as np

from _base import *

class Fuzzbox(AudioEffect):
    """FuzzFace based on model at http://www.geofex.com/effxfaq/distn101.htm
    
    Parameters:
        Amount --   A factor from 0 to 5.0 representing the 
                     amount of distortion to add."""
    name = 'Fuzzbox'
    description = 'Asymetrical distortion'
    
    def __init__(self):
        super(Fuzzbox, self).__init__()
        self.parameters = {'Amount':Parameter(float, 1, 5, 1)}
    
    def process_data(self, data):
        a = self.parameters['Amount'].value
        return np.piecewise(data, [data > 0, data < 0], [lambda x: x * a, lambda x: x / a, 0])
