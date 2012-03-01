import numpy as np

from _base import *

class Overdrive(AudioEffect):
    name = 'Overdrive'
    description = 'Non-linear distortion'
    
    def __init__(self):
        super(Overdrive, self).__init__()
        self.parameters = {'Amount':Parameter(float, 0.1, 0.75, 0.75, inverted=True),
                           'Sensitivity':Parameter(float, 0.01, 1, 1, inverted=True)}
    
    def sigmoid_vector(self):
        #a knee of 0.75 results in approxamately linear amplification for -0.5 < x < 0.5
        knee = self.parameters['Amount'].value
        def f(x):
            return  x / (x * x + knee)
        return np.vectorize(f)
    
    def process_data(self, data):
        #normalize the data before applying the amplification
        normal_factor = SAMPLE_MAX * self.parameters['Sensitivity'].value
        return self.sigmoid_vector()(data / normal_factor) * normal_factor
