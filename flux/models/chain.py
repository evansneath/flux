#!/usr/bin/env python

"""chain.py

This module defines the AudioChain structure and its node classes.
"""

# Library imports
import sndobj
import effect
import time

class AudioChain(object):
    """AudioChain class
    
    Organizes the audio effect chain data structure.
    """
    def __init__(self):
        """Initialization function for a new Chain object."""
        super(AudioChain, self).__init__()
        # Define audio thread.
        self.__thread = sndobj.SndThread()
        # Define input (adc) and output (dac) objects.
        self.__input = effect.AudioIn()
        self.__output = effect.AudioOut()
        # Route output from the given input object.
        self.__output.dac.SetOutput(1, self.__input._signal)
        # List to store all defined effects.
        self.__effect_list = list()
    
    def add(self, new_effect):
        """Adds a new effect to the effect chain.
        
        Arguments:
            effect: The effect subclass object to add.
        Returns:
            True upon successful add, False if unsuccessful.
        """
        if issubclass(type(new_effect), effect.Effect):
            self.__effect_list.append(new_effect)
            return True
        else:
            return False
    
    def remove(self, index):
        """Removes an effect from the effect chain.
        
        Arguments:
            index: The index of the effect to remove from the chain.
        Returns:
            The effect that was removed.
        """
        if index in self.__effect_list:
            del_effect = self.__effect_list[index]
            self.__effect_list.remove(index)
        else:
            del_effect = None
        return del_effect
    
    def compile(self):
        """Links all effects and allows the AudioChain to be processed."""
        # Add dac and adc to the sound thread
        self.__thread.AddObj(self.__input.adc, sndobj.SNDIO_IN)
        self.__thread.AddObj(self.__output.dac, sndobj.SNDIO_OUT)
        # Send the input signal to the thread output
        self.__thread.AddObj(self.__input._signal)
        # Add all effects to the thread output
        for e in self.__effect_list:
            self.__thread.AddObj(e._signal)
        return
    
    def start(self):
        """Begins the signal processing for the AudioChain object."""
        self.__thread.ProcOn()
        return
    
    def stop(self):
        """Ends the signal processing for the AudioChain object."""
        self.__thread.ProcOff()
        return

def main():
    print('hello, chain')
    
    # THIS IS A TEST OF THE AUDIOCHAIN CLASS
    c = AudioChain()
    c.compile()
    print('Starting')
    c.start()
    time.sleep(10)
    c.stop()
    print('Done')
    # END OF TEST
    
    return

if __name__ == '__main__':
    main()