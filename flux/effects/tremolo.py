import math

import numpy as np

from _base import *

class PulseModulation(AudioEffect):
    """Pulse Width Modulation effect

    Outputs a windowed, pulse-width modulation function with specified
    duration and duty cycle.

    Parameters:
        Duration -- The time of the total cycle (on + off time). [s]
        Duty     -- The percentage of on time of the signal. [%]
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

        # Determine if the duration or duty cycle parameters have been changed
        if (self._old_duration != duration or self._old_duty != duty):
            # Calculate the samples active and inactive during one cycle (duty)
            total_samples = duration * SAMPLE_RATE
            active_samples = math.floor(total_samples * duty)
            inactive_samples = total_samples - active_samples

            self._old_duration = duration
            self._old_duty = duty

            # Create a new array with the specified duty cycle and speed
            on_cycle = np.ones(active_samples) * np.hamming(active_samples)
            off_cycle = np.zeros(inactive_samples)
            self._mod = np.concatenate([on_cycle, off_cycle])
        else:
            # Continue to modulate the signal with the old carrier signal
            self._mod = np.roll(self._mod, self._old_data_size)

        # Store the data size to roll the carrier signal in the next run
        self._old_data_size = data.size

        # Perform the signal modulation
        return np.multiply(data, np.resize(self._mod, (data.size,)))

class Tremelo(AudioEffect):
    """Tremelo effect

    Outputs a signal with low-frequency modulation using a specified signal
    type and speed.

    Parameters:
        Speed -- The length of a period of the carrier signal. [s]
        Shape -- The waveform of the carrier signal. (Sin, Sawtooth, Square)
        Mix   -- The Wet/Dry mix ratio. [%]
    """
    name = 'Tremelo'
    description = 'Modulates the time signal, creating a vibrato effect.'

    def __init__(self):
        super(Tremelo, self).__init__()

        self.carrier = None

        self.parameters = {'Speed':Parameter(float, 1.0, 10.0, 3.0),
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
            self.carrier = np.sin(np.linspace(0, np.pi, period / 2))
        elif shape == 'Sawtooth':
            sawtooth = np.linspace(0, 1, period / 2)
            # Smooth out the wave a bit by multiplying it with it's complement raised to a large power
            complement = 1 - np.power(sawtooth, 20)
            # This is 1 / max(complement) when the exponent is 20, and is used to keep a constant maximum amplitude
            normalization_factor = 1.2226448438558761
            self.carrier = sawtooth * complement * normalization_factor
        elif shape == 'Square':
            # Create a rounded square wave by multiplying 1-sawtooth(-x)**20, which rises sharply at x=0
            # and 1-sawtooth(x)**20, which falls sharply at the half period
            sawtooth = np.linspace(0, 1, period / 2)
            sawtooth_neg = np.linspace(1, 0, period / 2)
            square = (1 - np.power(sawtooth, 20)) * (1 - np.power(sawtooth_neg, 20))
            self.carrier = np.concatenate([square, np.zeros(period / 2)])
        else:
            print 'Error, unknown carrier shape:', shape

    def process_data(self, data):
        mix = self.parameters['Mix'].value
        wet = data * np.resize(self.carrier, len(data))
        self.carrier = np.roll(self.carrier, -len(data))

        return ((1 - mix) * data) + (mix * wet)
