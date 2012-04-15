import numpy as np
import scipy.signal as signal

from _base import *

class BasicFilter(AudioEffect):
    """Creates a basic filter function using an IIR filter design.
    
    Parameters:
        center -- The center frequency of the filter function. [Hz]
        type -- The filter function type (LP, HP, BP, BS)
    """
    
    name = 'Basic Filter'
    description = 'Filters the incoming signal using an IIR filter design.'
    
    def __init__(self):
        super(BasicFilter, self).__init__()
        self.parameters = {'Center':Parameter(float, 20, NYQUIST, 5000),
                           'Type':DiscreteParameter({'LP':'', 'HP':'', 'BP':'', 'BS':''}, 'LP')}
        self.parameters['Center'].value_changed.connect(self.param_changed_event)
        self.parameters['Type'].value_changed.connect(self.param_changed_event)
        
        self._a = None # numerator filter coefficients
        self._b = None # denominator filter coefficients
        self._zi = None # zero input array
        self._zo = None # zero output array
        
        self.param_changed_event()
    
    def param_changed_event(self):
        # First get order and designed cutoff from specifications
        f0 = self.parameters['Center'].value
        type = self.parameters['Type'].value
        
        # Determine quality factor (Q) based on filter type
        if type == 'LP': Q = 0.8 # optimized
        elif type == 'HP': Q = 20 # optimized
        elif type == 'BP': Q = 0.8 # ok - could use work
        elif type == 'BS': Q = 5 # ok - gives around 1kHz stopband
        
        # Perform necessary calculations for filter coefficients
        w0 = np.pi * f0 / float(NYQUIST)
        cosw0 = np.cos(w0)
        sinw0 = np.sin(w0)
        alpha = sinw0 / (2 * Q)
        
        if type == 'LP':
            # Compute lowpass coefficients
            self._a = np.array([1 + alpha, -2 * cosw0, 1 - alpha])
            self._b = np.array([(1 - cosw0) / 2, 1 - cosw0, (1 - cosw0) / 2])
        elif type == 'HP':
            # Compute highpass coefficients
            self._a = np.array([1 + alpha, -2 * cosw0, 1 - alpha])
            self._b = np.array([(1 + cosw0) / 2, -(1 + cosw0), (1+ cosw0) / 2])
        elif type == 'BP':
            # Compute bandpass coefficients
            self._a = np.array([1 + alpha, -2 * cosw0, 1 - alpha])
            self._b = np.array([alpha, 0, -alpha])
        elif type == 'BS':
            # Compute bandstop (notch) coefficients
            self._a = np.array([1 + alpha, -2 * cosw0, 1 - alpha])
            self._b = np.array([1, -2 * cosw0, 1])
        
        # Compute zero input response
        self._zi = signal.lfilter_zi(self._b, self._a)
    
    def process_data(self, data):
        (out, self._zo) = signal.lfilter(self._b, self._a, data, axis=0, zi=self._zi)
        self._zi = self._zo
        return out