"""Collection of audio effects that process data contained in QByteArrays"""

import struct
import math
import time
import collections

import numpy as np
import scipy.signal as signal

from PySide import QtCore, QtMultimedia

SAMPLE_MAX = 32767
SAMPLE_MIN = -(SAMPLE_MAX + 1)
SAMPLE_RATE = 44100 # [Hz]
NYQUIST = SAMPLE_RATE / 2
SAMPLE_SIZE = 16 # [bit]
CHANNEL_COUNT = 1
BUFFER_SIZE = 2500 #this is the smallest buffer that prevents underruns on my machine


def samples_from_ms(milliseconds):
    return milliseconds * 0.001 * SAMPLE_RATE

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
            #t1 = time.clock() #for performance timing
            
            for effect in self.effects:
                if len(data): #empty arrays cause a crash
                    data = effect.process_data(data)
                    
            ####
            ##processing performace timing
            #t2 = time.clock() 
            #self.ts.append(t2-t1)
            #if len(self.ts) % 100 == 0:
            #    print sum(self.ts) / float(len(self.ts)) * 1000000, 'us'
            #    self.ts = []
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
    
    #Signal emited when value member changes
    value_changed = QtCore.Signal()
    
    def __init__(self, type=int, minimum=0, maximum=100, value=10, inverted=False):
        super(Parameter, self).__init__()
        
        #type must be a callable that will convert a value from a float to the desired type
        self.type = type
        self.minimum = minimum
        self.maximum = maximum
        self._value = value
        self.inverted = inverted
        
    def __repr__(self):
        return '%s(%s, %s, %s, %s, %i)' % (self.__class__.__name__, self.type, self.minimum, self.maximum, self.value, self.inverted)
        
    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, val):
        self._value = val
        self.value_changed.emit()
        

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

class DiscreteParameter(Parameter):
    """A Parameter with a set of discrete values instead of a range.
    
    Members:
        choices_dict -- a dictionary mapping names of available choices to their
                        optional icon file path if no icon is desired, the path
                        should be an empty string
        value        -- the name currently selected choice
    """

    def __init__(self, choices_dict, value):
        super(DiscreteParameter, self).__init__()
        self.choices_dict = collections.OrderedDict(choices_dict)
        self._value = value

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

class Delay(AudioEffect):
    """Delay"""
    name = 'Delay'
    description = 'One tap, 100ms-1s delay'
    
    def __init__(self):
        super(Delay, self).__init__()
        
        self.parameters = {'Delay':Parameter(int, samples_from_ms(100), samples_from_ms(1000), samples_from_ms(150)),
                           'Mix':Parameter(float, 0, 1, .5),
                           'Feedback':Parameter(float, 0, 1.1, .5)} #maximum feedback slightly greater than 1, be careful
        
        self.delay_line = None
        self.delay_changed_event()
        
        self.parameters['Delay'].value_changed.connect(self.delay_changed_event)

    def delay_changed_event(self):
        self.delay_line = np.zeros(self.parameters['Delay'].value)
        
    def process_data(self, data):
        wet = self.parameters['Mix'].value
        dry = 1 - wet
        mixin = self.delay_line[:len(data)] * wet
        self.delay_line[:len(data)] = data + mixin * self.parameters['Feedback'].value
        self.delay_line = np.roll(self.delay_line, -len(data))
        
        return (data * dry) + mixin
        
    
    
class Equalization(AudioEffect):
    """Equalization effect"""
    name = 'Equalization'
    description = ''
    
    _delta_f = 1 / SAMPLE_RATE
    
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
        self.parameters = {'Amount':Parameter(float, 0, 15, 1)}
    
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
        self.parameters = {'Cutoff':Parameter(int, 20, 22050, 20000)}
        self._old_cutoff = 0
        self._old_data_size = 0
        self._h_freq = np.array([])
    
    def process_data(self, data):
        cutoff = self.parameters['Cutoff'].value
        
        if cutoff != self._old_cutoff or data.size != self._old_data_size:
            h_bare = np.arange(-(data.size) / 2, (data.size) / 2)
            h_sinc = (2 * cutoff / SAMPLE_RATE) * np.sinc(np.multiply(2 * cutoff / SAMPLE_RATE, h_bare))
            h = np.multiply(np.hamming(data.size), h_sinc)
            self._h_freq = np.fft.fft(h)
            self._old_cutoff = cutoff
            self._old_data_size = data.size
        
        return np.fft.irfft(np.multiply(np.fft.fft(data), self._h_freq))
        
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
                           #'TempoParam 2':TempoParameter(),
                           #'Param2':Parameter(float, 0, 10, 5)}
                           'Style':DiscreteParameter({'Choice 1':'res/icons/control_play.png',
                                                      'Choice 2':'res/icons/wave_sine.png',
                                                      'Choice 3':'res/icons/wave_square.png',
                                                      '#4':''},
                                                    'Choice 2')}

class PulseModulation(AudioEffect):
    """Pulse Width Modulation effect.
    
    Parameters:
        duration -- The time of the total cycle (on + off time). [s]
        duty     -- The percentage of on time of the signal. [%]
    """
    name = 'Pulse Modulation'
    description = 'Introduces pulse width modulation to the signal.'
    
    def __init__(self):
        super(PulseModulation, self).__init__()
        self.parameters = {'Duration':Parameter(float, 0.0001, 1.0, 0.25),
                           'Duty':Parameter(float, 0.0001, 1.0, 0.5)}
        self._old_duration = 0.0
        self._old_duty = 0.0
        self._old_data_size = 0
        self._mod = np.array([])
    
    def process_data(self, data):
        duration = self.parameters['Duration'].value
        duty = self.parameters['Duty'].value
        
        if (self._old_duration != duration or self._old_duty != duty):
            total_samples = duration * SAMPLE_RATE
            active_samples = math.floor(total_samples * duty)
            inactive_samples = total_samples - active_samples
            
            self._old_duration = duration
            self._old_duty = duty
            
            self._mod = np.concatenate([np.ones(active_samples),
                                        np.zeros(inactive_samples)])
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
            tau = loop_time / 1000.0
            n = tau * SAMPLE_RATE
            g = (10.0 ** -3) ** (tau / duration)
            self._a = np.concatenate(([1], np.zeros(n), [-g]))
            self._b = np.array([1])
        
        out = signal.lfilter(self._b, self._a, data, axis=0)
        
        return out

class Tremelo(AudioEffect):
    """Tremelo effect.
    
    Parameters:
        Speed -- The length of a period of the carrier signal.
        Shape -- The waveform of the carrier signal.
        Mix   -- The Wet/Dry mix ratio.
    """
    name = 'Tremelo'
    description = 'Modulates the time signal, creating a vibrato effect.'
    
    def __init__(self):
        super(Tremelo, self).__init__()
        
        self.carrier = None
        
        self.parameters = {'Speed':Parameter(float, 2.0, 20.0, 5.0),
                           'Mix':Parameter(float, 0.0, 1, 0.25),
                           'Shape':DiscreteParameter({'Sin':'res/icons/wave_sine.png',
                                                      'Sawtooth':'res/icons/wave_saw.png',
                                                      'Square':'res/icons/wave_square.png'},
                                                    'Sin')}
        self.parameters['Speed'].value_changed.connect(self.carrier_changed_event)
        self.parameters['Shape'].value_changed.connect(self.carrier_changed_event)
        self.carrier_changed_event()
        
    def carrier_changed_event(self):
        shape = self.parameters['Shape'].value
        period = SAMPLE_RATE /  self.parameters['Speed'].value
        
        if shape == 'Sin':
            self.carrier = np.sin(np.linspace(0, 2 * np.pi, period))
        elif shape == 'Sawtooth':
            sawtooth = np.linspace(0, 1, period / 2)
            #smooth out the wave a bit by multiplying it with it's complement raised to a large power
            complement = 1 - np.power(sawtooth, 20)
            #this is 1 / max(complement) when the exponent is 20, and is used to keep a constant maximum amplitude 
            normalization_factor = 1.2226448438558761 
            self.carrier = sawtooth * complement * normalization_factor
        elif shape == 'Square':
            #create a rounded square wave by multiplying 1-sawtooth(-x)**20, which rises sharply at x=0
            #   and 1-sawtooth(x)**20, which falls sharply at the half period
            sawtooth = np.linspace(0, 1, period / 2)
            sawtooth_neg = np.linspace(1, 0, period / 2)
            square = (1 - np.power(sawtooth, 20)) * (1 - np.power(sawtooth_neg, 20))
            self.carrier = np.concatenate([square, np.zeros(period / 2)])
        else:
            print 'Error, unknown carrier shape:', shape
        
    def process_data(self, data):
        mix = self.parameters['Mix'].value
        wet = data * np.resize(self.carrier, data.size)
        self.carrier = np.roll(self.carrier, -data.size)
        
        return ((1 - mix) * data) + (mix * wet)

#this tuple needs to be maintained manually
available_effects = (Decimation, Delay, FoldbackDistortion, Fuzzer, Gain,
                     HysteresisGate, LowPass, NoiseGate, Overdrive, Passthrough,
                     PulseModulation, Reverb, Tremelo)

