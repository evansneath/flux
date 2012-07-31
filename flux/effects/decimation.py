import numpy as np

from _base import *

class Decimation(AudioEffect):
    """Decimation / Bitcrushing effect.

    Creates an 8-bit sound using a combination of bitrate crushing and sample
    rate reduction.

    Parameters:
        Bitrate     -- Amount of bit accuracy in the output data. [bits]
        Sample Rate -- Sample rate reduction of the output data. [Hz]
    """
    name = 'Decimation'
    description = 'Reduce signal sample rate and/or bit accuracy'

    def __init__(self):
        super(Decimation, self).__init__()
        self.parameters = {'Bitrate':Parameter(int, 0, SAMPLE_SIZE, 0, inverted=True),
                           'Sample rate':Parameter(int, 1, 25, 1, inverted=True)}

    def process_data(self, data):
        # Truncate input data by shifting right, then left
        shift_amount = self.parameters['Bitrate'].value
        data = np.left_shift(np.right_shift(data.real.astype(int), shift_amount), shift_amount)
        # Reduce sample rate by skipping the specified number of samples
        reduc_amount = self.parameters['Sample rate'].value
        return np.repeat(data[::reduc_amount], reduc_amount)[:len(data)].astype(float)
