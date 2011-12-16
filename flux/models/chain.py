#!/usr/bin/env python

"""chain.py

This module defines the AudioChain structure and its node classes.
"""

# Library imports
import sndobj
import effect

class AudioChain(object):
    """AudioChain class
    
    Organizes the audio effect chain data structure.
    """
    def __init__(self):
        """Initialization function for a new Chain object."""
        super(Chain, self).__init__()
        thread = sndobj.SndThread()
        input = AudioIn()
        output = AudioOut()
        effect_list = List()
    
    def add(effect):
        """Adds a new effect to the effect chain.
        
        Arguments:
            effect: The effect subclass object to add.
        Returns:
            True upon successful add, False if unsuccessful.
        """
        if issubclass(type(effect), Effect):
            effect_list.append(effect)
            return True
        else:
            return False
    
    def remove(index):
        """Removes an effect from the effect chain.
        
        Arguments:
            index: The index of the effect to remove from the chain.
        Returns:
            The effect that was removed.
        """
        if index in effect_list:
            del_effect = effect_list[index]
            effect_list.remove(index)
        else:
            del_effect = None
        return del_effect
    
    def compile():
        """Links all effects and allows the AudioChain to be processed."""
        thread.AddObj(input.adc, sndobj.SNDIO_IN)
        thread.AddObj(output.dac, sndobj.SNDIO_OUT)
        thread.AddObj(input._signal)
        for e in effect_list:
            thread.AddObj(e._signal)
        return
    
    def start():
        """Begins the signal processing for the AudioChain object."""
        thread.ProcOn()
        return
    
    def stop():
        """Ends the signal processing for the AudioChain object."""
        thread.ProcOff()
        return

def main():
    print('hello, chain')
    return

if __name__ == '__main__':
    main()