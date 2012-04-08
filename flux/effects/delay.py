import numpy as np

from _base import *

def samples_from_ms(milliseconds):
    return milliseconds * 0.001 * SAMPLE_RATE

class Delay(AudioEffect):
    """Delay"""
    name = 'Delay'
    description = 'One tap, 100ms-1s delay'
    
    def __init__(self):
        super(Delay, self).__init__()
        
        self.parameters = {'Delay':Parameter(int, samples_from_ms(100), samples_from_ms(1000), samples_from_ms(150)),
                           'Mix':Parameter(float, 0, 1, .5),
                           'Feedback':Parameter(float, 0, 1, .5)}
        
        self.delay_line = None
        self.delay_changed_event()
        
        self.parameters['Delay'].value_changed.connect(self.delay_changed_event)

    def delay_changed_event(self):
        self.delay_line = np.zeros(self.parameters['Delay'].value)
        
    def process_data(self, data):
        wet = self.parameters['Mix'].value
        dry = 1 - wet
        mixin = self.delay_line[:len(data)] * wet
        self.delay_line[:len(data)] = data + mixin * self.parameters['Feedback'].value
        self.delay_line = np.roll(self.delay_line, -len(data))
        
        return (data * dry) + mixin
