import numpy as np

from _base import *

class PitchShift(AudioEffect):
    """Pitch Shift effect

    Modifies the original signal by shifting the pitch up. This utilizes the
    single-sideband amplitude modulation method.

    Parameters:
        Frequency -- The frequency amount to shift the original signal.
    """
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

        # Initialize the sin and cos signals with the specified modulation frequency
        self._mod_sin = np.sin(np.linspace(0, 2*np.pi, num=SAMPLE_RATE/f, endpoint=False))
        self._mod_cos = np.cos(np.linspace(0, 2*np.pi, num=SAMPLE_RATE/f, endpoint=False))

    def process_data(self, data):
        # Taper the input data using a hamming window method
        window = np.hamming(data.size)
        data *= window

        # SSB-AM: Single-Side Band Amplitude Modulation Method
        # output = data*Cos(2pi*Fc*t) + HilbertXF(data)*Sin(2pi*Fc*t)

        # First process data*Cos(2pi*Fc*t) portion of the equation
        part1 = np.multiply(data, np.resize(self._mod_cos, data.size))

        # Process the Hilbert transform of the signal
        # HilbertXF(data) = ifft(1j * fft(data) * sigmoid)
        data_spect = np.fft.fft(data, n=data.size)
        freq = np.fft.fftfreq(data.size, d=1/SAMPLE_RATE)
        data_hilbert = np.fft.ifft(1j * data_spect * np.sign(freq), n=data.size)

        # Process second portion of the equation. HilbertXF(data)*Sin(2pi*Fc*t)
        part2 = np.multiply(data_hilbert, np.resize(self._mod_sin, data.size))

        # Roll sin and cos functions to provide a uniform modulation
        self._mod_sin = np.roll(self._mod_sin, data.size)
        self._mod_cos = np.roll(self._mod_cos, data.size)

        # Add part one and two of the equation and use only the real portion
        return np.add(part1, part2).real
