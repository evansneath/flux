#!/usr/bin/env python

"""trait.py

This module contains and organizes trait objects.
"""

# Library imports
import sndobj

class Trait(object):
    """Trait class

    A trait object stores a single character trait relating
    to a parent effect.

    Attributes:
        parent: The trait's parent effect.
        name: The string formatted name of the trait.
    """
    def __init__(self, parent, name=''):
        """Initialization function for a new trait object.

        Arguments:
            parent: The trait's parent effect.
            name: The name of the trait.
        """
        super(Trait, self).__init__()
        self.__parent = parent
        self.__set_name(name)
        self.__signal
    
    def __lshift__(self, in_signal):
        """Overrides the '<<' operator to give signal input passing capability."""
        if issubclass(type(in_signal), Trait):
            self.__signal << in_signal.__signal
        else:
            # Add exception raise: InputDatatypeError
            return

    def __get_parent(self):
        """Getter for the trait parent. Parent value may
           not be changed as this trait is owned completely."""
        return self.__parent

    def __get_name(self):
        """Getter for the trait name."""
        return self.__name

    def __set_name(self, new_name):
        """Setter for the trait name."""
        if isinstance(new_name, str):
            self.__name = new_name
        else:
            # Add exception raise: InputDatatypeError
            return

    parent = property(fget=__get_parent, 
                      doc='Gets the parent effect name.')
    name = property(fget=__get_name, fset=__set_name,
                    doc='Gets or sets the trait name.')

class BandpassFilter(Trait):
    """BandpassFilter class
    
    Representing an effect bandpass filtering of the output signal.
    
    Attributes:
        parent: The bandpass filter trait's parent effect.
        name: The formatted name of the bandpass filter trait.
        frequency: The active bandpass frequency. [Hz]
        bandwidth: The throughput bandwidth of the bandpass filter. [Hz]
    """
    def __init__(self, parent, name='', frequency=0., bandwidth=0.):
        """Initialization function for a new BandpassFilter object.
        
        Arguments:
            parent: The bandpass filter trait's parent effect.
            name: The formatted name of the bandpass filter trait.
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
        else:
            # Add exception raise: InputDatatypeError
            return
        
        self.__frequency = new_frequency
    
    def __set_bandwidth(self):
        """Getter for the bandpass filter's bandwidth property. [Hz]"""
        return self.__bandwidth
    
    def __get_bandwidth(self, new_bandwidth):
        """Setter for the bandpass filter's bandwidth property. [Hz]"""
        if isinstance(new_bandwidth, float) and new_bandwidth >= 0.:
            self.__signal.SetBW(new_bandwidth)
        else:
            # Add exception raise: InputDatatypeError
            return
        
        self.__bandwidth = new_bandwidth

class Delay(Trait):
    """Delay class
    
    Representing an effect delay of the output signal.
    
    Attributes:
        parent: The delay trait's parent effect.
        name: The formatted name of the gain trait.
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
            parent: The delay trait's parent effect.
            name: The formatted name of the gain trait.
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
        else:
            # Add exception raise: InputDatatypeError
            return
        
        self.__max_delay = new_max_delay
    
    def __get_delay(self):
        """Getter for the delay's delay time property. [s]"""
        return self.__delay
    
    def __set_delay(self, new_delay):
        """Setter for the delay's delay time property. [s]"""
        if isinstance(new_delay, float) and new_delay >= 0.:
            self.__signal.SetDelayTime(new_delay)
        else:
            # Add exception raise: InputDatatypeError
            return
        
        self.__delay = new_delay
    
    def __get_feedback_gain(self):
        """Getter for the delay's feedback gain. [-]"""
        return self.__feedback_gain
    
    def __set_feedback_gain(self, new_feedback_gain):
        """Setter for the delay's feedback gain. [-]"""
        if isinstance(new_feedback_gain, float):
            self.__signal.SetFdbgain(new_feedback_gain)
        elif issubclass(type(new_feedback_gain), Trait):
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
        elif issubclass(type(new_feedforward_gain), Trait):
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
        elif issubclass(type(new_direct_gain), Trait):
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

class Gain(Trait):
    """Gain class
    
    Representing an effect gain of the output signal.
    
    Attributes:
        parent: The gain trait's parent effect.
        name: The string formatted name of the gain trait.
        level: The active level of the gain. [dB]
        multiplier: The multiplication factor of the gain. [-]
    """
    def __init__(self, parent, name='', gain=10., multiplier=1.):
        """Initialization function for a new Gain object.
        
        Arguments:
            parent: The gain trait's parent effect.
            name: The formatted name of the gain trait.
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
        else:
            # Add exception raise: InputDatatypeError
            return
        
        self.__level = new_level

    def __get_multiplier(self):
        """Getter for the gain multiplier property. [-]"""
        return self.__multiplier
    
    def __set_multiplier(self, new_multiplier):
        """Setter for the gain multiplier property. [-]"""
        if isinstance(new_multiplier, float):
            self.__signal.SetGainM(new_multiplier)
        else:
            # Add exception raise: InputDatatypeError
            return
        
        self.__multiplier = new_multiplier

    level = property(fget=__get_level, fset=__set_level,
                     doc='Gets or sets the gain level. [dB]')
    multiplier = property(fget=__get_multiplier, fset=__set_multiplier,
                          doc='Gets or sets the gain multiplier. [-]')

class Pan(Trait):
    """Pan class
    
    Represents and effect pan augmentation.
    
    Attributes:
        parent: The pan trait's parent effect.
        name: The formatted name of the pan trait.
        pan: The pan level from -1 (100% left) to 1 (100% right). [-]
    """
    def __init__(self, parent, name='', pan=0.):
        """Initializes the pan trait.
        
        Arguments:
            parent: The pan trait's parent effect.
            name: The formatted name of the pan trait.
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
        elif issubclass(type(new_pan), Trait):
            self.__signal.SetPan(0, new_pan.__signal)
        else:
            # Add exception raise: InputDatatypeError
            return
        
        self.__pan = new_pan
    
    pan = property(fget=__get_pan, fset=__set_pan,
                   doc="Gets and sets the pan levels. [-]")

class Phase(Trait):
    """Phase class
    
    Represents an effect phase augmentation.
    
    Attributes:
        parent: The phase trait's parent effect.
        name: The formatted name of the phase trait.
        frequency: The phasor frequency. [Hz]
        offset: Signal phase in fractions of a cycle. [-] (0-1.0)
    """
    def __init__(self, parent, name='', frequency=0., offset=0.):
        """Initializes the phase trait.
        
        Arguments:
            parent: The phase trait's parent effect.
            name: The string formatted name of the phase trait.
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
        elif issubclass(type(new_frequency), Trait):
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
        else:
            # Add exception raise: InputDatatypeError
            return
        
        self.__offset = new_offset

    frequency = property(fget=__get_frequency, fset=__set_frequency,
                         doc='Gets or sets the phase frequency. [Hz]')
    offset = property(fget=__get_offset, fset=__set_offset,
                      doc='Gets or sets the phase offset. [-] (0-1.0)')

# Main function for class file
# (should remain relatively unused outside of small-scale class testing)
def main():
    print('hello, trait')
    return

if __name__ == '__main__':
    main()