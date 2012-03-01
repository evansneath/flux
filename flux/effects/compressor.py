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
                           'Sensitivity':Parameter(int, 0, SAMPLE_MAX / 2, SAMPLE_MAX / 10)}
        
    def process_data(self, data):
        threshold = SAMPLE_MAX - self.parameters['Sensitivity'].value
        ratio = self.parameters['Amount'].value
        db_threshold = level_to_db(threshold)
        db_data = level_to_db(np.fabs(data))
        compression = lambda d: d * db_to_level(db_threshold - d + (d - db_threshold) / ratio)
        abs = np.piecewise(db_data, [db_data > db_threshold], [compression, lambda x: db_to_level(x)])
        return abs * np.sign(data)