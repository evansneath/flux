import numpy as np

from _base import *

class Fuzzbox(AudioEffect):
    """Fuzzbox effect

    FuzzFace based on model at http://www.geofex.com/effxfaq/distn101.htm

    Parameters:
        Mix -- The ratio of original to fuzzed signal. [-]
    """
    name = 'Fuzzbox'
    description = 'Asymetrical distortion'

    def __init__(self):
        super(Fuzzbox, self).__init__()
        self.parameters = {'Mix':Parameter(float, 1, 5, 1)}

    def process_data(self, data):
        a = self.parameters['Mix'].value * 5.
        return np.piecewise(data, [data > 0, data < 0], [lambda x: x * a, lambda x: x / a, 0])
