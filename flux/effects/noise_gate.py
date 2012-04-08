import numpy as np

from _base import *

class NoiseGate(AudioEffect):
    """A simple threshold gate without hysteresis"""
    
    name = 'Noise Gate'
    description = 'Basic noise gate (no hysteresis)'
    
    def __init__(self):
        super(NoiseGate, self).__init__()
        self.parameters = {'Attenuation':Parameter(float, 0, 1, 1, inverted=True),
                           'Threshold':Parameter(int, 0, SAMPLE_MAX / 100, SAMPLE_MAX / 200)}

    def process_data(self, data):
        data[data < self.parameters['Threshold'].value] *= self.parameters['Attenuation'].value
        return data

class HysteresisGate(AudioEffect):
    """A two-threshold gate with hysteresis"""
    
    name = 'Hysteresis Gate'
    description = 'Noise gate with hysteresis (slower)'
    
    def __init__(self):
        super(HysteresisGate, self).__init__()
        self.parameters = {'Attenuation':Parameter(float, 0, 1, 1, inverted=True),
                           'Pass Threshold':Parameter(int, 0, SAMPLE_MAX / 100, SAMPLE_MAX / 200),
                           'Mute Threshold':Parameter(int, 0, SAMPLE_MAX / 100, SAMPLE_MAX / 300)}
        
    def process_data(self, data):
        multiplier = self.parameters['Attenuation'].value
        low = self.parameters['Mute Threshold'].value
        high = self.parameters['Pass Threshold'].value
        
        muted = True
        for i in xrange(len(data)):
            if muted:
                if -high <= data[i] <= high:
                    data[i] *= multiplier
                else:
                    muted = False
            else:
                if -low <= data[i] <= low:
                    muted = True
                    data[i] *= multiplier
        return data