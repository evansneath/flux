import numpy as np

from _base import *

def level_to_db(data):
    return 20 * np.log10(data)
    
def db_to_level(data):
    return np.power(10, data / 20)

class Compressor(AudioEffect):
    name = 'Compressor'
    description = 'Dynamic range compression'
    
    def __init__(self):
        super(Compressor, self).__init__()
        self.parameters = {'Amount':Parameter(float, 1, 5, 1),
                           'Sensitivity':Parameter(int, 0, SAMPLE_MAX / 4, SAMPLE_MAX / 10)}
        self.parameters['Sensitivity'].value_changed.connect(self.sensitivity_changed_event)
        
        self.compress = lambda x:x
        self.sustain = lambda x:x
        self.upper_threshold_db = 0
        self.lower_threshold_db = 0
        self.sensitivity_changed_event()
        
    def sensitivity_changed_event(self):
        self.upper_threshold_db = level_to_db(SAMPLE_MAX - self.parameters['Sensitivity'].value)
        self.lower_threshold_db = level_to_db(self.parameters['Sensitivity'].value)
        
        ratio = self.parameters['Amount'].value
        self.compress = lambda d: db_to_level(self.upper_threshold_db + (d - self.upper_threshold_db) / ratio)
        self.sustain = lambda d: db_to_level(self.lower_threshold_db - (self.lower_threshold_db - d) / ratio)
        
    def process_data(self, data):
        db_data = level_to_db(np.fabs(data))
        
        abs = np.piecewise(db_data, [db_data > self.upper_threshold_db, db_data < self.lower_threshold_db],
                                    [self.compress, self.sustain, db_to_level])
        return abs * np.sign(data)