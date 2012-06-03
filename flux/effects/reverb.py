import numpy as np

from _base import *

def samples_from_ms(milliseconds):
    return milliseconds * 0.001 * SAMPLE_RATE

class Reverb(AudioEffect):
    """Reverb"""
    name = 'Reverb'
    description = 'Reverb'
    
    def __init__(self):
        super(Reverb, self).__init__()
        
        self.parameters = {'Amount':Parameter(float, 0, 0.5, .1)}
        self.delay = samples_from_ms(75
                                     )
        self.feedback = 0.5
        
        self.delay_line = None
        self.delay_changed_event()
        
        #self.parameters['Delay'].value_changed.connect(self.delay_changed_event)

    def delay_changed_event(self):
        self.delay_line = np.zeros(self.delay)
        
    def process_data(self, data):
        wet = self.parameters['Amount'].value
        dry = 1 - wet
        mixin = self.delay_line[:len(data)] * wet
        self.delay_line[:len(data)] = data + mixin * self.feedback
        self.delay_line = np.roll(self.delay_line, -len(data))
        return (data * dry) + mixin
