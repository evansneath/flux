import numpy as np

from _base import *

class Decimation(AudioEffect):
    """Decimation / Bitcrushing effect.
        
    Parameters:
        bits -- Amount of bit accuracy in the output data.
        rate -- Sample rate of the output data.
    """
    name = 'Decimation'
    description = 'Reduce signal sample rate and/or bit accuracy'
    
    def __init__(self):
        super(Decimation, self).__init__()
        self.parameters = {'Bitrate':Parameter(int, 0, SAMPLE_SIZE, 0, inverted=True),
                           'Sample rate':Parameter(int, 1, 25, 1, inverted=True)}
    
    def process_data(self, data):
        shift_amount = self.parameters['Bitrate'].value
        data = np.left_shift(np.right_shift(data.real.astype(int), shift_amount), shift_amount)
        reduc_amount = self.parameters['Sample rate'].value
        #there's probably a more fine-grained way to reduce the sample rate
        return np.repeat(data[::reduc_amount], reduc_amount)[:len(data)].astype(float)
