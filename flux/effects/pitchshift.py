import numpy as np
import scipy.signal as signal

from _base import *

class PitchShift(AudioEffect):
    name = 'PitchShift'
    description = 'Frequency shifting in the time domain'
    
    def __init__(self):
        super(PitchShift, self).__init__()
        self.parameters = {'Frequency':Parameter(float, 1, 5000, 50)}
        self.parameters['Frequency'].value_changed.connect(self.param_changed_event)
        self._mod_sin = None
        self._mod_cos = None
        self.param_changed_event()
    
    def param_changed_event(self):
        f = self.parameters['Frequency'].value
        self._mod_sin = np.sin(np.linspace(0, 2*np.pi, num=SAMPLE_RATE/f, endpoint=False))
        self._mod_cos = np.cos(np.linspace(0, 2*np.pi, num=SAMPLE_RATE/f, endpoint=False))
    
    def process_data(self, data):
        # SSB-AM <=> Single-Side Band Amplitude Modulation Method
        # output = data*Cos(2pi*Fc*t) + HilbertXF(data)*Sin(2pi*Fc*t)
        part1 = np.multiply(data, np.resize(self._mod_cos, data.size))
        
        data_spect = np.fft.fft(data, n=data.size)
        freq = np.fft.fftfreq(data.size, d=1/SAMPLE_RATE)
        data_spect = 1j * data_spect * np.sign(freq)
        data_hilbert = np.fft.ifft(data_spect, n=data.size)
        #data_hilbert = self._hilbert(data)
        
        part2 = np.multiply(data_hilbert, np.resize(self._mod_sin, data.size))
        self._mod_sin = np.roll(self._mod_sin, data.size)
        self._mod_cos = np.roll(self._mod_cos, data.size)
        return np.add(part1, part2).real
    
    def _hilbert(self, x):
        N = x.size
        n = np.arange(start=0, stop=x.size)
        
        h = (1 / (2 * np.pi * (n - (N - 1) / 2))) * (1 - np.cos(np.pi * (n - (N - 1) / 2)))
        H = np.fft.fft(h, n=h.size)
        X = np.fft.fft(x, n=x.size)
        Y = np.multiply(X, H)
        y = np.fft.ifft(Y, n=x.size)
        return y