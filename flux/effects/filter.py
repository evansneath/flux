import numpy as np
import scipy.signal as signal

from _base import *

class HighPass(AudioEffect):
    """Creates a high-pass filter using an IIR butterworth filter design.
    
    Parameters:
        cutoff -- The frequency to pass through. All lower frequencies are cut off. [Hz]
    """
    name = 'High-Pass Filter'
    description = 'Creates a high-pass filter using IIR Butterworth filter design.'
    
    def __init__(self):
        super(HighPass, self).__init__()
        self.parameters = {'Cutoff':Parameter(float, 20, NYQUIST, 5000)}
        self.parameters['Cutoff'].value_changed.connect(self.param_changed_event)
        
        self._a = None
        self._b = None
        self._zi = None
        self._zo = None
        self.param_changed_event()
    
    def param_changed_event(self):
        # First get order and designed cutoff from specifications
        cutoff = self.parameters['Cutoff'].value
        transition = cutoff * 0.2 / NYQUIST # Hz / Hz
        passband = cutoff / NYQUIST # passband frequency
        stopband = passband - transition # stopband frequency
        
        if stopband < 0.0: stopband = 0.01 # clip stopband frequency at 0 Hz
        
        passband = 0.35 #Hz
        stopband = 0.5 #Hz
        gpass = 3
        gstop = 15
        
        order = 3
        natural = 1000
        
        (self._b, self._a) = signal.iirfilter(order, natural, btype='highpass', ftype='butter', output='ba')
        self._zi = signal.lfilter_zi(self._b, self._a)
    
    def process_data(self, data):
        (out, self._zo) = signal.lfilter(self._b, self._a, data, zi=self._zi)
        self._zi = self._zo
        return out

class LowPass(AudioEffect):
    """Creates a low-pass filter using an IIR butterworth filter design.
    
    Parameters:
        cutoff -- The frequency to pass through. All higher frequencies are cut off. [Hz]
    """
    
    name = 'Low-Pass Filter'
    description = 'Creates a low-pass filter using IIR Butterworth filter design.'
    
    def __init__(self):
        super(LowPass, self).__init__()
        self.parameters = {'Cutoff':Parameter(float, 20, NYQUIST, 5000)}
        self.parameters['Cutoff'].value_changed.connect(self.param_changed_event)
        
        self._a = None
        self._b = None
        self._zi = None # zero input array
        self._zo = None # zero output array
        self.param_changed_event()
    
    def param_changed_event(self):
        # First get order and designed cutoff from specifications
        cutoff = self.parameters['Cutoff'].value
        transition = 2000 / NYQUIST # Hz / Hz
        passband = cutoff / NYQUIST # passband frequency
        stopband = passband + transition # stopband frequency
        
        if stopband > 0.99:
            stopband = 0.99 # clip stopband frequency at nyquist frequency
            passband = stopband - transition
        
        (order, natural) = signal.filter_design.buttord(passband, stopband, 3, 16, analog=0)
        (self._b, self._a) = signal.filter_design.butter(order, natural, btype='lowpass', analog=0, output='ba')
        self._zi = signal.lfilter_zi(self._b, self._a)
    
    def process_data(self, data):
        (out, self._zo) = signal.lfilter(self._b, self._a, data, axis=0, zi=self._zi)
        self._zi = self._zo
        return out