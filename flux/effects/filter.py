import collections

import numpy as np
import scipy.signal as signal

from _base import *

class BasicFilter(AudioEffect):
    """Creates a basic filter function using an IIR filter design.
    
    Parameters:
        center -- The center frequency of the filter function. [Hz]
        type -- The filter function type (LP, HP, BP, BS)
    """
    
    name = 'Basic Filters'
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

class Equalizer(AudioEffect):
    """Creates a test equalizer filter function using an IIR filter design.
    
    Parameters:
        low_gain -- The amplitude of the lowband frequency band. [%]
        mid_gain -- The amplitude of the midband frequency band. [%]
        high_gain -- The amplitude of the highband frequency band. [%]
    """
    
    name = '3-Band Equalizer'
    description = 'A test equalizer function using an IIR filter design.'
    
    def __init__(self):
        super(Equalizer, self).__init__()
        self.parameters = collections.OrderedDict((('Low',Parameter(float, 0., 2., 1.)),
                           ('Mid',Parameter(float, 0., 2., 1.)),
                           ('High',Parameter(float, 0., 2., 1.))))
        self.parameters['Low'].value_changed.connect(self.param_changed_event)
        self.parameters['Mid'].value_changed.connect(self.param_changed_event)
        self.parameters['High'].value_changed.connect(self.param_changed_event)
        
        # cutoff frequencies for eq filters
        self._lowfreq = 880
        self._highfreq = 5000
        
        self._lp = BasicFilter()
        self._lp.parameters['Type'].value = 'LP'
        self._lp.parameters['Center'].value = self._lowfreq
        
        self._hp = BasicFilter()
        self._hp.parameters['Type'].value = 'HP'
        self._hp.parameters['Center'].value = self._highfreq
        
        self.param_changed_event()
    
    def param_changed_event(self):
        self._low_gain = self.parameters['Low'].value
        self._mid_gain = self.parameters['Mid'].value
        self._high_gain = self.parameters['High'].value
    
    def process_data(self, data):
        l_data = self._lp.process_data(data)
        h_data = self._hp.process_data(data)
        m_data = data - (l_data + h_data)
        
        l_data *= self._low_gain
        h_data *= self._high_gain
        m_data *= self._mid_gain
        
        return (l_data + m_data + h_data)