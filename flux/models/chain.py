#!/usr/bin/env python

"""chain.py

This module defines the AudioChain class and its node classes.
"""

# Library imports
import effect
from sndobj import SndThread

class AudioChain(object):
    """AudioChain class
    
    Organizes and drives the effect objects and processing threads.
    
    Attributes:
        length: Number of effects in the chain.
    """
    def __init__(self):
        """Initialization function for a new AudioStack."""
        super(AudioStack, self).__init__()
        self.length = 0
        self.__input = None
        self.__output = None
        
        # Populate thread
        self.__thread = sndobj.SndThread()
        
        # Populate input
        if not self.link(AudioIn()):
            pass
        
        # Populate output
        if not self.link(AudioOut()):
            pass
    
    def link(self, effect, index=None):
        """Links a new effect onto the signal chain.
        
        Arguments:
            effect: An effect to link to the effects chain.
            index: The index to place the new effect to link. If none is given,
                   the effect is placed at the end of the chain.
        Returns:
            The index of the linked effect.
        """
        pass
    
    def unlink(self, index):
        """Unlinks a specified effect from the signal chain.
        
        Arguments:
            index: The index of the effect to unlink from the chain.
        Returns:
            The unlinked effect object.
        """
        pass
    
    def fork(self, index):
        """Splits (or forks) a chain into two output ends.
        
        Arguments:
            index: The index in the chain to place the fork.
        Returns:
            The index of the created fork.
        """
        pass
    
    def merge(self, index):
        """Merges two signals into one output end.
        
        Arguments:
            index: The index in the chain to place the merge.
        Returns:
            The index of the created merge.
        """
        pass
    
    def on():
        """Starts the chain signal processing.
        
        Returns:
            True on successful start. False on error.
        """
        pass
    
    def off():
        """Stops the chain signal processing thread.
        
        Returns:
            True on successful start. False on error.
        """
        pass

class AudioNode(object):
    def __init__(self):
        self.prev = None
        self.next = None
    pass

class EffectNode(AudioNode):
    def __init__(self):
        super(EffectNode, self).__init__()

class MergeNode(AudioNode):
    def __init__(self):
        super(MergeNode, self).__init__()

class ForkNode(AudioNode):
    def __init__(self):
        super(ForkNode, self).__init__()

def main():
    print('hello, chain')
    return

if __name__ == '__main__':
    main()