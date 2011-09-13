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
    """
    def __init__(self):
        """Initialization function for a new AudioChain object."""
        super(AudioChain, self).__init__()
        self.__nodes = dict()
        self.__id_ticker = 0
        self.__node_count = 0
        
        # Populate sound thread
        self.__thread = sndobj.SndThread()
    
    def link(self, effect, prev_id=None):
        """Links a new effect onto the signal chain.
        
        Arguments:
            effect: An effect to link to the effects chain.
            prev_id: The id of the chain node where the effect node should be
                attached. If none is defined, assumed to be first node.
        Returns:
            The id of the linked effect. None on failure.
        """
        # Verify that the node is either the first or references a previous
        # node. Return no created node id if this is the case.
        if prev_id not in self.__nodes and self.__node_count is not 0:
            return None
        
        # Verify effect payload.
        if effect is not instanceof(effect.Effect) \
            or not issubclass(effect, effect.Effect):
            return None
        
        # Increment the id ticker to provide a unique id to the new node.
        node_id, self.__id_ticker = self.__id_ticker + 1
        
        # Create new EffectNode and add to dictionary.
        self.__nodes[node_id] = EffectNode(node_id, prev_id, next_id, effect)
        self.__node_count += 1
        
        # TODO: Add special support for MergeNode and ForkNode previous and
        # next nodes when a node is added.
        
        # If the added node is not the first, adopt the previous node's next
        # node if it is defined.
        if self.__nodes[prev_id]:
            self.__nodes[node_id].next_id = self.__nodes[prev_id].next_id
            self.__nodes[prev_id].next_id = node_id
        
        # TODO: Add effect to the audio processing thread. Link new effect
        # input and output to the previous and next effect (if they exist).
        
        return node_id
    
    def unlink(self, node_id):
        """Unlinks a specified node from the signal chain.
        
        Arguments:
            node_id: The id of the node to unlink from the chain.
        Returns:
            The unlinked chain node.
        """
        pass
    
    def fork(self, prev_id):
        """Splits (or forks) a chain into two output ends.
        
        Arguments:
            prev_id: The id of the chain node where the fork node should be
                attached.
        Returns:
            The id of the created fork node.
        """
        pass
    
    def merge(self, prev_id):
        """Merges two separate node chains into one output end.
        
        Arguments:
            prev_id: The id of the chain node where the merge node should be
                attached.
        Returns:
            The id of the created merge node.
        """
        pass
    
    def start():
        """Starts the chain signal processing thread.
        
        Returns:
            True on successful start. False on error.
        """
        pass
    
    def stop():
        """Stops the chain signal processing thread.
        
        Returns:
            True on successful start. False on error.
        """
        pass

class ChainNode(object):
    def __init__(self, node_id, prev_id=None, next_id=None):
        """Initialization function for the generic ChainNode object.
        
        Arguments:
            node_id: The unique identifier for the node within the chain.
            prev_id: Reference to the previous node in the chain.
            next_id: Reference to the next node in the chain.
        """
        self.node_id = node_id
        self.prev_id = prev_id
        self.next_id = next_id
    
    def __str__(self):
        """Override string output."""
        print('ChainNode:{}'.format(self.node_id))

class EffectNode(ChainNode):
    def __init__(self, node_id, prev_id=None, next_id=None, effect=None):
        """Initialization function for the EffectNode object.
        
        Arguments:
            node_id: The unique identifier for the node in the chain.
            prev_id: Reference to the previous node in the chain.
            next_id: Reference to the next node in the chain.
            effect: The effect payload of the node.
        """
        super(EffectNode, self).__init__(node_id, prev_id, next_id)
        self.effect = effect
    
    def __str__(self):
        """Override string output."""
        print('EffectNode:{}'.format(self.node_id))

class MergeNode(ChainNode):
    def __init__(self, node_id, prev_id=[None, None], next_id=None):
        """Initialization function for ChainNode object.
        
        Arguments:
            node_id: The unique identifier for the node in the chain.
            prev_id: Reference to the two previous nodes in the chain to merge.
            next_id: Reference to the next node in the chian
        """
        super(MergeNode, self).__init__(node_id, prev_id, next_id)
    
    def __str__(self):
        """Override string output."""
        print('MergeNode:{}'.format(self.node_id))

class ForkNode(ChainNode):
    def __init__(self, node_id, prev_id=None, next_id=[None, None]):
        """Initialization function for ForkNode object.
        
        Arguments:
            node_id: The unique identifier for the node in the chain.
            prev_id: Reference to the previous node in the chain.
            next_id: Reference to the two next nodes in the chain to fork.
        """
        super(ForkNode, self).__init__(node_id, prev_id, next_id)
    
    def __str__(self):
        """Override string output."""
        print('ForkNode:{}'.format(self.node_id))

def main():
    print('hello, chain')
    return

if __name__ == '__main__':
    main()