import numpy as np

from _base import *

def level_to_db(data):
    return 20 * np.log10(data)

def db_to_level(data):
    return np.power(10, data / 20)

class Compressor(AudioEffect):
    """Compressor effect

    Flattens high-amplitude peaks across frequencies to obtain a more uniform sound.

    Parameters:
        Amount      -- The level at which the above-threshold peaks are reduced. [-]
        Sensitivity -- Determines the threshold frequency to flatten. [-]
    """
    name = 'Compressor'
    description = 'Peak limiting compressor'

    def __init__(self):
        super(Compressor, self).__init__()
        self.parameters = {'Amount':Parameter(float, 1, 5, 1),
                           'Sensitivity':Parameter(int, 0, SAMPLE_MAX / 4, SAMPLE_MAX / 10)}
        self.parameters['Sensitivity'].value_changed.connect(self.sensitivity_changed_event)

        self.compress = lambda x:x
        self.threshold_db = 0
        self.sensitivity_changed_event()

    def sensitivity_changed_event(self):
        self.threshold_db = level_to_db(SAMPLE_MAX - self.parameters['Sensitivity'].value)
        self.compress = lambda d: self.threshold_db + (d - self.threshold_db) / self.parameters['Amount'].value

    def process_data(self, data):
        db_data = level_to_db(np.fabs(data))
        indexes = db_data > self.threshold_db
        db_data[indexes] = self.compress(db_data[indexes])
        return db_to_level(db_data) * np.sign(data)

class Sustain(AudioEffect):
    """Sustain effect

    Creates a sustained (held) output signal.

    Parameters:
        Amount      -- The level at which the signal is sustained. [-]
        Sensitivity -- The threshold of the signal to sustain. [-]
    """
    name = 'Sustain'
    description = 'Small signal gain'

    def __init__(self):
        super(Sustain, self).__init__()
        self.parameters = {'Amount':Parameter(float, 1, 5, 1),
                           'Sensitivity':Parameter(int, 0, SAMPLE_MAX / 4, SAMPLE_MAX / 10)}
        self.parameters['Sensitivity'].value_changed.connect(self.sensitivity_changed_event)

        self.sustain = lambda x:x
        self.threshold_db = 0
        self.sensitivity_changed_event()

    def sensitivity_changed_event(self):
        self.threshold_db = level_to_db(self.parameters['Sensitivity'].value)
        self.sustain = lambda d: self.threshold_db - (self.threshold_db - d) / self.parameters['Amount'].value

    def process_data(self, data):
        db_data = level_to_db(np.fabs(data))
        indexes = db_data < self.threshold_db
        db_data[indexes] = self.sustain(db_data[indexes])
        return db_to_level(db_data) * np.sign(data)
