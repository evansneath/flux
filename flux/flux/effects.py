"""Collection of audio effects that process data contained in QByteArrays"""

import struct
import math
import time

import numpy as np

from PySide import QtCore, QtGui, QtMultimedia

SAMPLE_MAX = 32767
SAMPLE_MIN = -(SAMPLE_MAX + 1)
SAMPLE_RATE = 44100 # [Hz]

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
        format.setChannels(1)
        format.setChannelCount(1)
        format.setSampleSize(16)
        format.setSampleRate(44100)
        
        if not info.isFormatSupported(format):
            print 'Format not supported, using nearest available'
            format = nearestFormat(format)
            if format.sampleSize != 16:
                #this is important, since effects assume this sample size.
                raise RuntimeError('16-bit sample size not supported!')
        
        self.audio_input = QtMultimedia.QAudioInput(format, app)
        self.audio_output = QtMultimedia.QAudioOutput(format)
        
        self.source = None
        self.sink = None
        
        self.effects = []
        
    def start(self):
        self.source = self.audio_input.start()
        self.sink = self.audio_output.start()
        
        self.source.readyRead.connect(self.on_ready_read)
        
    def stop(self):
        self.audio_input.stop()
        self.audio_output.stop()
        
    def on_ready_read(self):
        #cast the input data as int32 while it's being processed so that it doesn't get clipped prematurely
        data = np.fromstring(self.source.readAll(), 'int16').astype(int)
        
        #t1 = time.clock() #for performance timing
        
        for effect in self.effects:
            if len(data): #empty arrays cause a crash
                data = effect.process_data(data)
                
        ###
        ##performance timing
        #t2 = time.clock() 
        #self.ts.append(t2-t1)
        #if len(self.ts) % 100 == 0:
        #    print sum(self.ts) / float(len(self.ts)) * 1000000, 'us'
        #    self.ts = []
        ###
        
        self.sink.write(data.clip(SAMPLE_MIN, SAMPLE_MAX).astype('int16').tostring())


class Parameter(QtCore.QObject):
    """A description of an effect parameter.
    
    Members:
        maximum -- The largest value that the parameter should contain.
        minumum -- The smallest value that the parameter should contain.
        value   -- The current value of the parameter. It is updated whenever the interface element changes.
        type    -- The type that value sould be stored as.
    """
    def __init__(self, type=int, minimum=0, maximum=100, value=10):
        super(Parameter, self).__init__()
        
        #type must be a callable that will convert a value from a float to the desired type
        self.type = type
        self.minimum = minimum
        self.maximum = maximum
        self.value = value

class AudioEffect(QtCore.QObject):
    """Base class for audio effects."""
    name = 'Unknown Effect'
    description = ''
    
    def __init__(self):
        """parameters -- A dictionary of str(param_name):Parameter items that describes all parameters that a user can alter."""
        super(AudioEffect, self).__init__()
        self.parameters = {}
    
    def process_data(self, data):
        """Modify a numpy.aray and return the modified array.
        
        This is an abstract method to represent data processing. Override this
        function when subclassing AudioEffect.
        """
        return data

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
        self.parameters = {'Bitrate reduction':Parameter(int, 0, 16, 0),
                           'Sample rate reduction':Parameter(int, 1, 10, 1)}
    
    def process_data(self, data):
        shift_amount = self.parameters['Bitrate reduction'].value
        data = np.left_shift(np.right_shift(data, shift_amount), shift_amount)
        reduc_amount = self.parameters['Sample rate reduction'].value
        #there's probably a more fine-grained way to reduce the sample rate
        return np.repeat(data[::reduc_amount], reduc_amount)[:len(data)]

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
        return np.multiply(data, self.parameters['Amount'].value).astype(int)

class GenericFilter(AudioEffect):
    """An effect for testing FFT"""
    name = 'GenericFilter'
    description = 'Testing fft and filtering'

    def __init__(self):
        super(GenericFilter, self).__init__()
        self.parameters = {'Amount':Parameter(float, 0, 10, 1)}
        
    def process_data(self, data):
        modified_data = np.fft.rfft(data)
        freq = np.fft.fftfreq(modified_data.size)
        H = np.divide(1,1 + np.multiply(self.parameters['Amount'].value,freq))
        
        return np.fft.irfft(np.multiply(modified_data,H))
    
class Passthrough(AudioEffect):
    """An effect for testing"""
    
    name = 'Passthrough'
    description = 'Does not modify the signal'
    
    def __init__(self):
        super(Passthrough, self).__init__()
        self.parameters = {'Param 1':Parameter(float, 0, 10, 5),
                           'Param 2':Parameter()}

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
        self.parameters = {'Duration':Parameter(float, 0.0, 1.0, 0.25),
                           'Duty':Parameter(float, 0.0, 1.0, 0.5)}
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
            self._mod = np.roll(self._mod, -self._old_data_size)
        
        self._old_data_size = data.size
        return np.multiply(data, np.resize(self._mod, (1, data.size)))

#this tuple needs to be maintained manually
available_effects = (Decimation, FoldbackDistortion, Gain, GenericFilter, Passthrough, PulseModulation)
