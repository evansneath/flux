"""Collection of audio effects that process data contained in QByteArrays"""

import struct
import math
import time
import collections

import numpy as np
from scipy.signal import lfilter, filter_design

from PySide import QtCore, QtGui, QtMultimedia

SAMPLE_MAX = 32767
SAMPLE_MIN = -(SAMPLE_MAX + 1)
SAMPLE_RATE = 44100 # [Hz]
NYQUIST = SAMPLE_RATE / 2
SAMPLE_SIZE = 16 # [bit]
CHANNEL_COUNT = 1
BUFFER_SIZE = 2500 #this is the smallest buffer that prevents underruns on my machine

class AudioPath(QtCore.QObject):
    """Class that handles audio input and output and applying effects.
    
    Parameters:
    app -- a QApplication or QCoreApplication
    """
    ts = [] #for performance timing
    def __init__(self, app):
        super(AudioPath, self).__init__()
        
        info = QtMultimedia.QAudioDeviceInfo.defaultInputDevice()
        format = info.preferredFormat()
        format.setChannels(CHANNEL_COUNT)
        format.setChannelCount(CHANNEL_COUNT)
        format.setSampleSize(SAMPLE_SIZE)
        format.setSampleRate(SAMPLE_RATE)
        
        if not info.isFormatSupported(format):
            print 'Format not supported, using nearest available'
            format = nearestFormat(format)
            if format.sampleSize != SAMPLE_SIZE:
                #this is important, since effects assume this sample size.
                raise RuntimeError('16-bit sample size not supported!')
        
        self.audio_input = QtMultimedia.QAudioInput(format, app)
        self.audio_input.setBufferSize(BUFFER_SIZE)
        self.audio_output = QtMultimedia.QAudioOutput(format)
        
        self.source = None
        self.sink = None
        
        self.processing_enabled = True
        
        self.effects = []
    
    def start(self):
        self.processing_enabled = True
        
        self.source = self.audio_input.start()
        self.sink = self.audio_output.start()
        
        self.source.readyRead.connect(self.on_ready_read)
    
    def stop(self):
        self.audio_input.stop()
        self.audio_output.stop()
    
    def on_ready_read(self):
        #cast the input data as int32 while it's being processed so that it doesn't get clipped prematurely
        data = np.fromstring(self.source.readAll(), 'int16').astype(float)
        
        if self.processing_enabled:
            t1 = time.clock() #for performance timing
            
            for effect in self.effects:
                if len(data): #empty arrays cause a crash
                    data = effect.process_data(data)
                    
            ####
            ##processing performace timing
            t2 = time.clock() 
            self.ts.append(t2-t1)
            if len(self.ts) % 100 == 0:
                print sum(self.ts) / float(len(self.ts)) * 1000000, 'us'
                self.ts = []
            ####
            ##time between on_ready_read calls
            #self.ts.append(time.clock())
            #if len(self.ts) % 100 == 0:
            #    print (sum(self.ts[i] - self.ts[i-1] for i in range(1, len(self.ts))) / (len(self.ts) - 1)) * 1000, 'ms'
            #    self.ts = []
            #        
            ###
        
        self.sink.write(data.clip(SAMPLE_MIN, SAMPLE_MAX).astype('int16').tostring())

class Parameter(QtCore.QObject):
    """A description of an effect parameter.
    
    Members:
        maximum  -- The largest value that the parameter should contain.
        minumum  -- The smallest value that the parameter should contain.
        value    -- The current value of the parameter. It is updated whenever the interface element changes.
        type     -- The type that value sould be stored as.
        inverted -- If True, a slider at the highest position will produce the minimum value and vice versa.
    """
    def __init__(self, type=int, minimum=0, maximum=100, value=10, inverted=False):
        super(Parameter, self).__init__()
        
        #type must be a callable that will convert a value from a float to the desired type
        self.type = type
        self.minimum = minimum
        self.maximum = maximum
        self.value = value
        self.inverted = inverted

class TempoParameter(Parameter):
    """A Parameter whose value can be overridden by a user supplied tempo, in beats-per-minute.
    
    If use_bpm is True, value will be an integer with 0 < value < 1000.
    Otherwise value will be a value adhering to minumum, maximum and type, as usual.
    """
    bpm = 0
    
    def __init__(self, type=int, minimum=0, maximum=100, value=10):
        super(TempoParameter, self).__init__(type, minimum, maximum, value)
        
        self._value = value
        self.use_bpm = False
    
    @property
    def value(self):
        if self.use_bpm:
            return self.bpm
        return self._value
    
    @value.setter
    def value(self, val):
        self._value = val

    @classmethod
    def set_bpm(cls, value):
        cls.bpm = value
        
    def set_use_bpm(self, value):
        self.use_bpm = value

class AudioEffect(QtCore.QObject):
    """Base class for audio effects."""
    name = 'Unknown Effect'
    description = ''
    
    def __init__(self):
        """parameters -- A dictionary of str(param_name):Parameter items that describes all parameters that a user can alter."""
        super(AudioEffect, self).__init__()
        self.parameters = {}
    
    def process_data(self, data):
        """Modify a numpy.array and return the modified array.
        
        This is an abstract method to represent data processing. Override this
        function when subclassing AudioEffect.
        """
        return data

class Compressor(AudioEffect):
    name = 'Compressor'
    description = 'Hard Knee, Instant Attck'
    
    def __init__(self):
        super(Compressor, self).__init__()
        self.parameters = {'Amount':Parameter(float, 1, 5, 1),
                           'Threshold':Parameter(int, 0, SAMPLE_MAX / 2, SAMPLE_MAX / 10)}
        
    def process_data(self, data):
        tl = self.parameters['Threshold'].value
        th = SAMPLE_MAX - tl
        a = self.parameters['Amount'].value
        return np.piecewise(data,
                            [data > th, data < -th, (0 < data) & (data < tl)],
                            [lambda x: th + (x - th) / a, lambda x: -th + (th + x) / a,
                             lambda x: x + (tl - x) / a, #this is still wrong
                             lambda x: x])

class Decimation(AudioEffect):
    """Decimation / Bitcrushing effect.
        
    Parameters:
        bits -- Amount of bit accuracy in the output data.
        rate -- Sample rate of the output data.
    """
    name = 'Decimation'
    description = 'Reduce signal sample rate and/or bit accuracy'
    
    def __init__(self):
        super(Decimation, self).__init__()
        self.parameters = {'Bitrate':Parameter(int, 0, SAMPLE_SIZE, 0, inverted=True),
                           'Sample rate':Parameter(int, 1, 25, 1, inverted=True)}
    
    def process_data(self, data):
        shift_amount = self.parameters['Bitrate'].value
        data = np.left_shift(np.right_shift(data.real.astype(int), shift_amount), shift_amount)
        reduc_amount = self.parameters['Sample rate'].value
        #there's probably a more fine-grained way to reduce the sample rate
        return np.repeat(data[::reduc_amount], reduc_amount)[:len(data)].astype(float)

class Equalization(AudioEffect):
    """Equalization effect"""
    name = 'Equalization'
    description = ''
    
    def __init__(self):
        super(Equalization, self).__init__()
        self._delta_f = 1 / SAMPLE_RATE
    
    def process_data(self, data):
        spectrum = np.fft.fft(data * np.hanning(data.size))
        frequency = np.fft.fftfreq(data.size)
        
        return np.fft.ifft(spectrum).real

class FoldbackDistortion(AudioEffect):
    """Foldback distortion
    
    Parameters:
        threshold -- A factor from 0 to SAMPLE_MAX representing the 
                     maximum allowed value before the signal is clipped.
    """
    name = 'Foldback Distortion'
    description = 'A rudimentary distortion utilizing a threshold amplitude.'
    
    def __init__(self):
        super(FoldbackDistortion, self).__init__()
        self.parameters = {'Threshold':Parameter(int, 1, SAMPLE_MAX, SAMPLE_MAX)}
    
    def process_data(self, data):
        threshold=self.parameters['Threshold'].value
        def func(value, threshold=threshold):
            return int(math.fabs(math.fabs(math.fmod(
                    value - threshold, threshold * 4)) -
                    threshold * 2) - threshold)
        vec = np.vectorize(func)
        return np.piecewise(data, [data < -threshold, data > threshold], [vec, vec, lambda x: x])

class Fuzzer(AudioEffect):
    """FuzzFace based on model at http://www.geofex.com/effxfaq/distn101.htm
    
    Parameters:
        Amount --   A factor from 0 to 5.0 representing the 
                     amount of distortion to add."""
    name = 'Fuzzer'
    description = 'Asymetrical distortion'
    
    def __init__(self):
        super(Fuzzer, self).__init__()
        self.parameters = {'Amount':Parameter(float, 1, 5, 1)}
    
    def process_data(self, data):
        a = self.parameters['Amount'].value
        return np.piecewise(data, [data > 0, data < 0], [lambda x: x * a, lambda x: x / a, 0])

class Gain(AudioEffect):
    """Gain effect
    
    Parameters:
       amount -- A factor by which to multiply the input signal. Unintended
                 clipping can occur if multiplied values exceed 16-bit integer
                 maximum. 
    """
    name = 'Gain'
    description = 'Increase the volume, clipping loud signals'
    
    def __init__(self):
        super(Gain, self).__init__()
        self.parameters = {'Amount':Parameter(float, 0, 10, 1)}
    
    def process_data(self, data):
        return np.multiply(data, self.parameters['Amount'].value)

class GenericFilter(AudioEffect):
    """An effect for testing FFT"""
    name = 'Generic Filter'
    description = 'Testing fft and filtering'

    def __init__(self):
        super(GenericFilter, self).__init__()
        self.parameters = {'Amount':Parameter(float, 0, 10, 1)}
        
    def process_data(self, data):
        modified_data = np.fft.rfft(data)
        freq = np.fft.fftfreq(modified_data.size)
        H = np.divide(1,1 + np.multiply(self.parameters['Amount'].value,freq))
        
        return np.fft.irfft(np.multiply(modified_data,H)).real

class NoiseGate(AudioEffect):
    """A simple threshold gate without hysteresis"""
    
    name = 'Noise Gate'
    description = 'Basic noise gate (no hysteresis)'
    
    def __init__(self):
        super(NoiseGate, self).__init__()
        self.parameters = {'Attenuation':Parameter(float, 0, 1, 1, inverted=True),
                           'Threshold':Parameter(int, 0, SAMPLE_MAX / 100, SAMPLE_MAX / 200)}

    def process_data(self, data):
        data[data < self.parameters['Threshold'].value] *= self.parameters['Attenuation'].value
        return data

class HysteresisGate(AudioEffect):
    """A two-threshold gate with hysteresis"""
    
    name = 'Hysteresis Gate'
    description = 'Noise gate with hysteresis (slower)'
    
    def __init__(self):
        super(HysteresisGate, self).__init__()
        self.parameters = {'Attenuation':Parameter(float, 0, 1, 1, inverted=True),
                           'Pass Threshold':Parameter(int, 0, SAMPLE_MAX / 100, SAMPLE_MAX / 200),
                           'Mute Threshold':Parameter(int, 0, SAMPLE_MAX / 100, SAMPLE_MAX / 300)}
        
    def process_data(self, data):
        multiplier = self.parameters['Attenuation'].value
        low = self.parameters['Mute Threshold'].value
        high = self.parameters['Pass Threshold'].value
        
        muted = True
        for i in xrange(len(data)):
            if muted:
                if -high <= data[i] <= high:
                    data[i] *= multiplier
                else:
                    muted = False
            else:
                if -low <= data[i] <= low:
                    muted = True
                    data[i] *= multiplier
        return data

class LowPass(AudioEffect):
    """Creates a low-pass filter using windowing in frequency domain.
    
    Parameters:
        cutoff -- The frequency to pass through. All higher frequencies are cut off.
    """
    
    name = 'Low-Pass Filter'
    description = 'Creates a low-pass filter using windowing in the frequency domain.'
    
    def __init__(self):
        super(LowPass, self).__init__()
        self.parameters = {'Cutoff':Parameter(int, 20, NYQUIST, 16000)}
        self._old_cutoff = 0
        self._old_data_size = 0
        self._h_freq = np.array([])
    
    def process_data(self, data):
        cutoff = self.parameters['Cutoff'].value
        
        if cutoff != self._old_cutoff or data.size != self._old_data_size:
            h_bare = np.arange(-(data.size) / 2, (data.size) / 2)
            h_sinc = np.multiply(2 * cutoff / SAMPLE_RATE, np.sinc(np.multiply(2 * cutoff / SAMPLE_RATE, h_bare)))
            h = np.multiply(np.hamming(data.size), h_sinc)
            self._h_freq = np.fft.fft(h)
            
            self._old_cutoff = cutoff
            self._old_data_size = data.size
        
        return np.fft.irfft(np.multiply(np.fft.fft(data), self._h_freq))

class LowPassButterworth(AudioEffect):
    """Creates a low-pass filter using an IIR butterworth filter design.
    
    Parameters:
        cutoff -- The frequency to pass through. All higher frequencies are cut off.
    """
    
    name = 'Low-Pass Butterworth Filter'
    description = 'Creates a low-pass filter using IIR Butterworth filter design.'
    
    def __init__(self):
        super(LowPassButterworth, self).__init__()
        self.parameters = {'Cutoff':Parameter(float, 20, NYQUIST, 17000),
                           'Transition':Parameter(float, 0.001, 0.1, 0.1)}
        self._old_cutoff = 0
        self._old_transition = 0
        self._a = np.array([])
        self._b = np.array([])
    
    def process_data(self, data):
        cutoff = self.parameters['Cutoff'].value
        transition = self.parameters['Transition'].value 
        
        if cutoff != self._old_cutoff or transition != self._old_transition:
            # First get order and designed cutoff from specifications
            omega_p = float(cutoff) / NYQUIST # passband
            omega_s = omega_p + transition # stopband
            #if omega_s > 1.0: omega_s = 1.0
            print 'OMEGAp:', omega_p, 'OMEGAs: ', omega_s
            (order, omega_n) = filter_design.buttord(omega_p, omega_s, -2, -6, analog=0)
            print 'ORDER: ', order
            (self._b, self._a) = filter_design.butter(order, omega_n, btype='low', analog=0, output='ba')
            
            self._old_cutoff = cutoff
            self._old_transition = transition
        
        return lfilter(self._b, self._a, data)

class Overdrive(AudioEffect):
    name = 'Overdrive'
    description = 'Non-linear distortion'
    
    def __init__(self):
        super(Overdrive, self).__init__()
        self.parameters = {'Amount':Parameter(float, 0.1, 0.75, 0.75, inverted=True),
                           'Sensitivity':Parameter(float, 0.01, 1, 1, inverted=True)}
    
    def sigmoid_vector(self):
        #a knee of 0.75 results in approxamately linear amplification for -0.5 < x < 0.5
        knee = self.parameters['Amount'].value
        def f(x):
            return  x / (x*x + knee)
        return np.vectorize(f)
    
    def process_data(self, data):
        #normalize the data before applying the amplification
        normal_factor = SAMPLE_MAX * self.parameters['Sensitivity'].value
        return self.sigmoid_vector()(data / normal_factor) * normal_factor

class Passthrough(AudioEffect):
    """An effect for testing"""
    
    name = 'Passthrough'
    description = 'Does not modify the signal'
    
    def __init__(self):
        super(Passthrough, self).__init__()
        self.parameters = {'Param':Parameter(float, 0, 10, 5),
                           'TempoParam 1':TempoParameter(),
                           'TempoParam 2':TempoParameter()}

class PulseModulation(AudioEffect):
    """Pulse Width Modulation effect.
    
    Parameters:
        duration  -- The time of the total cycle (on + off time). [s]
        duty      -- The percentage of on time of the signal. [%]
        intensity -- The level of dropoff of the signal on the low cycle. [-]
    """
    name = 'Pulse Modulation'
    description = 'Introduces pulse width modulation to the signal.'
    
    def __init__(self):
        super(PulseModulation, self).__init__()
        self.parameters = {'Duration':Parameter(float, 0.0001, 1.0, 0.25),
                           'Duty':Parameter(float, 0.0001, 1.0, 0.5),
                           'Intensity':Parameter(float, 0.0001, 0.9, 0.5, True)}
        self._old_duration = 0.0
        self._old_duty = 0.0
        self._old_intensity = 0.0
        self._old_data_size = 0
        self._mod = np.array([])
    
    def process_data(self, data):
        duration = self.parameters['Duration'].value
        duty = self.parameters['Duty'].value
        intensity = self.parameters['Intensity'].value
        
        if (self._old_duration != duration or self._old_duty != duty or self._old_intensity != intensity):
            total_samples = duration * SAMPLE_RATE
            active_samples = math.floor(total_samples * duty)
            inactive_samples = total_samples - active_samples
            
            self._mod = np.concatenate([np.ones(active_samples),
                                        np.add(np.zeros(inactive_samples), intensity)])
            
            self._old_duration = duration
            self._old_duty = duty
            self._old_intensity = intensity
        else:
            self._mod = np.roll(self._mod, self._old_data_size)
        
        self._old_data_size = data.size
        return np.multiply(data, np.resize(self._mod, (data.size,)))

class Reverb(AudioEffect):
    """Reverberation effect.
    
    Parameters:
        loop_time -- Time between repetitions of the instantaneous signal. [ms]
        duration -- Total time of the reverb from start to fade out. [s]
    """
    name = 'Reverb'
    description = 'Passes the signal through a comb filter creating a feedback reverberation effect.'
    
    def __init__(self):
        super(Reverb, self).__init__()
        self.parameters = {'LoopTime':Parameter(float, 1, 1000.0, 1.0),
                           'Duration':Parameter(float, 0.1, 10.0, 2.0)}
        self._old_loop_time = 0
        self._old_duration = 0
        self._a = np.array([])
        self._b = np.array([])
    
    def process_data(self, data):
        loop_time = self.parameters['LoopTime'].value
        duration = self.parameters['Duration'].value
        
        if (loop_time != self._old_loop_time or duration != self._old_duration):
            #tau = loop_time / 1000.0
            #n = tau * SAMPLE_RATE
            #g = (10.0 ** -3) ** (tau / duration)
            
            # TEST BLOCK #############
            n = math.floor(SAMPLE_RATE * 0.0005)
            g = 0.8
            ##########################
            
            self._a = np.concatenate(([1], np.zeros(n), [-g]))
            self._b = np.array([1])
            
            # TEST BLOCK #############
            print 'N: ', n
            print 'G: ', g
            print 'A.SHAPE: ', self._a.shape
            print 'B.SHAPE: ', self._b.shape
            ##########################
            
            self._old_loop_time = loop_time
            self._old_duration = duration
        
        out = lfilter(self._b, self._a, data)
        
        return out

class Tremelo(AudioEffect):
    """Tremelo effect.
    
    Parameters:
        speed -- The length of a cycle of the tremelo. [s]
        intensity -- The of the signal magnitude varied by the tremelo. [%]
    """
    name = 'Tremelo'
    description = 'Modulates the time signal with sinusoidal wave, creating a vibrato effect.'
    
    def __init__(self):
        super(Tremelo, self).__init__()
        self.parameters = {'Speed':Parameter(float, 3.0, 10.0, 5.0),
                           'Intensity':Parameter(float, 0.0, 0.8, 0.25)}
        self._old_speed = 0.0
        self._old_intensity = 0.0
        self._old_data_size = 0
    
    def process_data(self, data):
        speed = self.parameters['Speed'].value
        intensity = self.parameters['Intensity'].value
        
        if (self._old_speed != speed or self._old_intensity != intensity):
            # create the modification array as a sine wave. At max, the tremelo
            # speed will be 1 second and intensity ranges from 0 to 1.
            self._old_speed = speed
            self._old_intensity = intensity
            
            self._mod = np.add(1 - intensity, np.multiply(intensity, np.cos(
                np.linspace(0, 2 * np.pi, num=((1 / speed) * SAMPLE_RATE),
                            endpoint=True))))
        else:
            self._mod = np.roll(self._mod, -self._old_data_size)
        
        self._old_data_size = data.size
        return np.multiply(data, np.resize(self._mod, (data.size,)))

#this tuple needs to be maintained manually
available_effects = (Equalization, Compressor, Decimation, FoldbackDistortion, Fuzzer, Gain,
                     GenericFilter, HysteresisGate, LowPass, LowPassButterworth, NoiseGate,
                     Overdrive, Passthrough, PulseModulation, Reverb, Tremelo)