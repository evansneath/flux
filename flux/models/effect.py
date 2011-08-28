#!/usr/bin/env python

"""effect.py

This module defines the Effect class and its subclass types.
"""

# Library imports
import sndobj

class Effect(object):
    """Effect class

    A effect object stores a single effect relating
    to modify a parent pedal. This is a base class.

    Attributes:
        parent: The effect's parent pedal object.
        name: The string formatted name of the effect.
    """
    def __init__(self, parent, name=''):
        """Initialization function for a new effect object.
        
        Arguments:
            parent: The effect's parent pedal object.
            name: The name of the effect.
        """
        super(Effect, self).__init__()
        self.__parent = parent
        self.__set_name(name)
        self.__signal
    
    def __rshift__(self, out_signal):
        """Overrides the '>>' operator to give signal input passing capability."""
        if isinstance(out_signal, AudioOut):
            # If the signal going out is to the output DAC, then set the last
            # signal to DAC output
            out_signal.__signal.SetOutput(1, self.__signal)
            out_signal.__signal.SetOutput(2, self.__signal)
        elif issubclass(type(out_signal), Effect):
            # Add the previous signal to the output signal
            out_signal.__signal += self.__signal
        else:
            # Add exception raise: InputDatatypeError
            return

    def __get_parent(self):
        """Getter for the parent pedal object."""
        return self.__parent

    def __get_name(self):
        """Getter for the effect name."""
        return self.__name

    def __set_name(self, new_name):
        """Setter for the effect name."""
        if isinstance(new_name, str):
            self.__name = new_name
        else:
            # Add exception raise: InputDatatypeError
            return

    parent = property(fget=__get_parent, 
                      doc='Gets the parent pedal name.')
    name = property(fget=__get_name, fset=__set_name,
                    doc='Gets or sets the effect name.')

class AudioIn(Effect):
    """AudioIn class
    
    The start point for the signal effects. Allows for signal input from the
    analog to digital converter.
    
    Attributes:
        parent: The effect's parent pedal object.
    """
    def __init__(self, parent):
        """
        Initialization function for the AudioOut object.
        
        Arguments:
            parent: The effect's parent pedal object.
        """
        super(AudioIn, self).__init__(parent, name='In')
        #TODO(evan): Put the adc determination in its own function. This will
        #            be variable depending on the system being run on.
        self.__adc = sndobj.SndRTIO(2, sndobj.SND_INPUT)
        self.__signal = sndobj.SndIn(self.__adc)
    
    def __get_adc(self):
        """Getter for the AudioIn object's analog to digital converter"""
        return self.__adc
    
    adc = property(fget=__get_adc,
                   doc="Gets the analog-to-digital converter.")

class AudioOut(Effect):
    """AudioOut class
    
    The end point for the signal effects. Allows for signal output to the
    digital to analog converter.
    
    Attributes:
        parent: The effect's parent pedal object.
    """
    def __init__(self, parent):
        """
        Initialization function for the AudioOut object.
        
        Arguments:
            parent: The effect's parent pedal object.
        """
        super(AudioOut, self).__init__(parent, name='Out')
        self.__signal = sndobj.SndRTIO(2, sndobj.SND_OUTPUT)
    
    def __rshift__(self, out_signal):
        # Do not allow right bitshift operator
        # Raise invalid operator exception
        return
    
    def __get_dac(self):
        """Getter for the AudioOut object's digital to analog converter"""
        return self.__signal
    
    dac = property(fget=__get_dac,
                   doc="Gets the digital-to-analog converter.")

class BandpassFilter(Effect):
    """BandpassFilter class
    
    Representing an pedal bandpass filtering of the output signal.
    
    Attributes:
        parent: The bandpass filter effect's parent pedal object.
        name: The formatted name of the bandpass filter effect.
        frequency: The active bandpass frequency. [Hz]
        bandwidth: The throughput bandwidth of the bandpass filter. [Hz]
    """
    def __init__(self, parent, name='', frequency=0., bandwidth=0.):
        """Initialization function for a new BandpassFilter object.
        
        Arguments:
            parent: The bandpass filter effect's parent pedal object.
            name: The formatted name of the bandpass filter effect.
            frequency: The active bandpass frequency. [Hz]
            bandwidth: The throughput bandwidth of the bandpass filter. [Hz]
        """
        super(BandpassFilter, self).__init__(parent, name)
        self.__signal = sndobj.Filter()
        self.__set_frequency(frequency)
        self.__set_bandwidth(bandwidth)
    
    def __get_frequency(self):
        """Getter for the bandpass filter's frequency property. [Hz]"""
        return self.__frequency
    
    def __set_frequency(self, new_frequency):
        """Setter for the bandpass filter's frequency property. [Hz]"""
        if isinstance(new_frequency, float) and new_frequency >= 0.:
            self.__signal.SetFreq(new_frequency)
            self.__frequency = new_frequency
        else:
            # Add exception raise: InputDatatypeError
            return
    
    def __set_bandwidth(self):
        """Getter for the bandpass filter's bandwidth property. [Hz]"""
        return self.__bandwidth
    
    def __get_bandwidth(self, new_bandwidth):
        """Setter for the bandpass filter's bandwidth property. [Hz]"""
        if isinstance(new_bandwidth, float) and new_bandwidth >= 0.:
            self.__signal.SetBW(new_bandwidth)
            self.__bandwidth = new_bandwidth
        else:
            # Add exception raise: InputDatatypeError
            return
    
class Delay(Effect):
    """Delay class
    
    Representing an pedal delay of the output signal.
    
    Attributes:
        parent: The delay effect's parent pedal object.
        name: The formatted name of the gain effect.
        max_delay: The maximum time delay of the signal. [s]
        delay: Delay time added to the signal. [s]
        feedback_gain: Gain factor of the signal reentering the delay. [-]
        feedforward_gain: Gain factor of the forward fed signal. [-] 
        direct_gain: Gain factor of the delay bypass signal. [-]
    """
    def __init__(self, parent, name='', max_delay=0., delay=0.,
                 feedback_gain=0., feedforward_gain=0., direct_gain=0.):
        """Initialization function for a new Delay object.
        
        Arguments:
            parent: The delay effect's parent pedal object.
            name: The formatted name of the gain effect.
            max_delay: The maximum time delay of the signal. [s]
            delay: Delay time added to the signal. [s]
            feedback_gain: Gain factor of the signal reentering the delay. [-]
            feedforward_gain: Gain factor of the forward fed signal. [-] 
            direct_gain: Gain factor of the delay bypass signal. [-]
        """
        super(Delay, self).__init__(parent, name)
        self.__signal = sndobj.VDelay()
        self.__set_max_delay(max_delay)
        self.__set_delay(delay)
        self.__set_feedback_gain(feedback_gain)
        self.__set_feedforward_gain(feedforward_gain)
        self.__set_direct_gain(direct_gain)
    
    def __get_max_delay(self):
        """Getter for the delay's maximum delay time property. [s]"""
        return self.__max_delay
    
    def __set_max_delay(self, new_max_delay):
        """Setter for the delay's maximum delay time property. [s]"""
        if isinstance(new_max_delay, float) and new_max_delay >= 0.:
            self.__signal.SetMaxDelayTime(new_max_delay)
            self.__max_delay = new_max_delay
        else:
            # Add exception raise: InputDatatypeError
            return
    
    def __get_delay(self):
        """Getter for the delay's delay time property. [s]"""
        return self.__delay
    
    def __set_delay(self, new_delay):
        """Setter for the delay's delay time property. [s]"""
        if isinstance(new_delay, float) and new_delay >= 0.:
            self.__signal.SetDelayTime(new_delay)
            self.__delay = new_delay
        else:
            # Add exception raise: InputDatatypeError
            return
    
    def __get_feedback_gain(self):
        """Getter for the delay's feedback gain. [-]"""
        return self.__feedback_gain
    
    def __set_feedback_gain(self, new_feedback_gain):
        """Setter for the delay's feedback gain. [-]"""
        if isinstance(new_feedback_gain, float):
            self.__signal.SetFdbgain(new_feedback_gain)
        elif issubclass(type(new_feedback_gain), Effect):
            self.__signal.SetFdbgain(0, new_feedback_gain.__signal)
        else:
            # Add exception raise: InputDatatypeError
            return
        
        self.__feedback_gain = new_feedback_gain
    
    def __get_feedforward_gain(self):
        """Getter for the delay's forward gain. [-]"""
        return self.__feedforward_gain
    
    def __set_feedforward_gain(self, new_feedforward_gain):
        """Setter for the delay's forward fed gain. [-]"""
        if isinstance(new_feedforward_gain, float):
            self.__signal.SetFwdgain(new_feedforward_gain)
        elif issubclass(type(new_feedforward_gain), Effect):
            self.__signal.SetFwdgain(0, new_feedforward_gain.__signal)
        else:
            # Add exception raise: InputDatatypeError
            return
        
        self.__feedforward_gain = new_feedforward_gain
    
    def __get_direct_gain(self):
        """Getter for the delay's direct gain. [-]"""
        return self.__direct_gain
    
    def __set_direct_gain(self, new_direct_gain):
        """Setter for the delay's direct gain. [-]"""
        if isinstance(new_direct_gain, float):
            self.__signal.SetDirgain(new_direct_gain)
        elif issubclass(type(new_direct_gain), Effect):
            self.__signal.SetDirgain(0, new_direct_gain.__signal)
        else:
            # Add exception raise: InputDatatypeError
            return
        
        self.__direct_gain = new_direct_gain
    
    max_delay = property(fget=__get_max_delay, fset=__set_max_delay,
                         doc="Gets and sets the maximum delay time. [s]")
    delay = property(fget=__get_delay, fset=__set_delay,
                     doc="Gets and sets the delay time. [s]")
    feedback_gain = property(fget=__get_feedback_gain,
                             fset=__set_feedback_gain,
                             doc="Gets and sets the delay's \
                                feedback gain. [-]")
    feedforward_gain = property(fget=__get_feedforward_gain,
                                fset=__set_feedforward_gain,
                                doc="Gets and sets the delay's \
                                    forward gain. [-]")
    direct_gain = property(fget=__get_direct_gain, fset=__set_direct_gain,
                           doc="Gets and sets the delay's direct gain. [-]")

class Gain(Effect):
    """Gain class
    
    Representing an pedal gain of the output signal.
    
    Attributes:
        parent: The gain effect's parent pedal.
        name: The string formatted name of the gain effect.
        level: The active level of the gain. [dB]
        multiplier: The multiplication factor of the gain. [-]
    """
    def __init__(self, parent, name='', gain=10., multiplier=1.):
        """Initialization function for a new Gain object.
        
        Arguments:
            parent: The gain effect's parent pedal.
            name: The formatted name of the gain effect.
            level: The active level of the gain. [dB]
            multiplier: The multiplication factor of the gain. [-]
        """
        super(Gain, self).__init__(parent, name)
        self.__signal = sndobj.Gain()
        self.__set_level(level)
        self.__set_multiplier(multiplier)

    def __get_level(self):
        """Getter for the gain level property. [dB]"""
        return self.__level
    
    def __set_level(self, new_level):
        """Setter for the gain level property. [dB]"""
        if isinstance(new_level, float):
            self.__signal.SetGain(new_level)
            self.__level = new_level
        else:
            # Add exception raise: InputDatatypeError
            return

    def __get_multiplier(self):
        """Getter for the gain multiplier property. [-]"""
        return self.__multiplier
    
    def __set_multiplier(self, new_multiplier):
        """Setter for the gain multiplier property. [-]"""
        if isinstance(new_multiplier, float):
            self.__signal.SetGainM(new_multiplier)
            self.__multiplier = new_multiplier
        else:
            # Add exception raise: InputDatatypeError
            return

    level = property(fget=__get_level, fset=__set_level,
                     doc='Gets or sets the gain level. [dB]')
    multiplier = property(fget=__get_multiplier, fset=__set_multiplier,
                          doc='Gets or sets the gain multiplier. [-]')

class Pan(Effect):
    """Pan class
    
    Represents and pedal pan augmentation.
    
    Attributes:
        parent: The pan effect's parent pedal object.
        name: The formatted name of the pan effect.
        pan: The pan level from -1 (100% left) to 1 (100% right). [-]
    """
    def __init__(self, parent, name='', pan=0.):
        """Initializes the pan effect.
        
        Arguments:
            parent: The pan effect's parent pedal object.
            name: The formatted name of the pan effect.
            pan: The pan level from -1 (100% left) to 1 (100% right). [-]
        """
        super(Pan, self).__init__(parent, name)
        self.__signal = sndobj.Pan()
        self.__set_pan(pan)
    
    def __get_pan(self):
        """Getter for the pan property"""
        return self.__pan
    
    def __set_pan(self, new_pan):
        """Setter for the pan property"""
        if isinstance(new_pan, float) and new_pan <= 1. and new_pan >= -1.:
            self.__signal.SetPan(new_pan)
        elif issubclass(type(new_pan), Effect):
            self.__signal.SetPan(0, new_pan.__signal)
        else:
            # Add exception raise: InputDatatypeError
            return
        
        self.__pan = new_pan
    
    pan = property(fget=__get_pan, fset=__set_pan,
                   doc="Gets and sets the pan levels. [-]")

class Phase(Effect):
    """Phase class
    
    Represents an pedal phase augmentation.
    
    Attributes:
        parent: The phase effect's parent pedal object.
        name: The formatted name of the phase effect.
        frequency: The phasor frequency. [Hz]
        offset: Signal phase in fractions of a cycle. [-] (0-1.0)
    """
    def __init__(self, parent, name='', frequency=0., offset=0.):
        """Initializes the phase effect.
        
        Arguments:
            parent: The phase effect's parent pedal object.
            name: The string formatted name of the phase effect.
            frequency: The phasor frequency. [Hz]
            offset: Initial phase offset in fractions of a cycle. [-] (0-1.0)
        """
        super(Phase, self).__init__(parent, name)
        self.__signal = sndobj.Phase()
        self.__set_frequency(frequency)
        self.__set_offset(offset)

    def __get_frequency(self):
        """Getter for the phasor frequency property."""
        return self.__frequency
    
    def __set_frequency(self, new_frequency):
        """Setter for the phasor frequency property."""
        if isinstance(new_frequency, float) and new_frequency >= 0.:
            self.__signal.SetFreq(new_frequency)
        elif issubclass(type(new_frequency), Effect):
            self.__signal.SetFreq(0, new_frequency)
        else:
            # Add exception raise: InputDatatypeError
            return
        
        self.__frequency = new_frequency

    def __get_offset(self):
        """Getter for the phase offset property."""
        return self.__offset

    def __set_offset(self, new_offset):
        """Setter for the phase offset property."""
        if (isinstance(new_offset, float) and new_offset >= 0.
            and new_offset <= 1.):
            self.__signal.SetPhase(new_offset)
            self.__offset = new_offset
        else:
            # Add exception raise: InputDatatypeError
            return

    frequency = property(fget=__get_frequency, fset=__set_frequency,
                         doc='Gets or sets the phase frequency. [Hz]')
    offset = property(fget=__get_offset, fset=__set_offset,
                      doc='Gets or sets the phase offset. [-] (0-1.0)')

# Main function for class file
# (should remain relatively unused outside of small-scale class testing)
def main():
    print('hello, effect')
    return

if __name__ == '__main__':
    main()