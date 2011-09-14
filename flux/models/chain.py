#!/usr/bin/env python

"""chain.py

This module defines the generic Chain structure and its node classes.
"""

class Chain(object):
    """Chain class
    
    Organizes the chain data structure.
    """
    def __init__(self):
        """Initialization function for a new Chain object."""
        super(Chain, self).__init__()
        self.__head_id = None
        self.__tail_id = None
        
        self.__nodes = dict()
        self.__id_ticker = 0
    
    def add(self, payload):
        """Adds a new payload node onto the end of the chain.
        
        Arguments:
            payload: An effect to add to the effects chain.
        Returns:
            The id of the added effect. None on failure.
        """
        node_id = self.__id_ticker
        
        if not self.__nodes.items():
            # If the dictionary is empty, this is the head node.
            self.__head_id = node_id
        else:
            # Update current pointed node's next value to the new node's id.
            self.__nodes[self.__tail_id].next_id = node_id
        
        self.__nodes[node_id] = ChainNode(next_id=None, payload=payload)
        self.__tail_id = node_id
        self.__id_ticker += 1
        
        return node_id
    
    def remove(self, node_id):
        """Removes a specified node from the chain.
        
        Arguments:
            node_id: The id of the node to remove from the chain.
        Returns:
            The payload of the removed chain node. None on failure.
        """
        # Determine if the node id inputted exists.
        if node_id not in self.__nodes:
            return None
        
        # Get all next id references to the node to be deleted.
        reference_list = self._find_by_next_id(node_id)
        for reference_node_id in reference_list:
            # Changed those nodes' next ids to the next id of the removed node.
            self.__nodes[reference_node_id].next_id = \
                self.__nodes[node_id].next_id
        
        # The payload should be saved to return from the function.
        old_payload = self.__nodes[node_id].payload
        # Delete the object to ensure no unreferenced nodes.
        del(self.__nodes[node_id])
        
        return old_payload
    
    def find_by_id(self, node_id):
        """Searches for a specified node id from the chain.
        
        Arguments:
            node_id: The id of the node to search for.
        Returns:
            The node payload object if found, None if not found.
        """
        if self.__nodes.has_key(node_id):
            return self.__nodes[node_id].payload
        else:
            return None
    
    def find_all(self):
        """Returns all currently present nodes.
        
        Arguments:
            None
        Returns:
            The list of all nodes currently contained within the chain.
        """
        return self.__nodes.keys()
    
    def _find_by_next_id(self, node_id):
        """Searches for next_id references to the specified node_id.
        
        Arguments:
            node_id: The id of the node which to search for references to.
        Returns:
            A list of node ids which reference the node_id node.
        """
        found = list()
        for node in self.__nodes.items():
            if node[1].next_id is node_id:
                found.append(node[0])
        return found
    
    def __get_count(self):
        """Getter for the node count property."""
        return len(self.__nodes)
    
    count = property(fget=__get_count, doc='Gets the node count.')

class ChainNode(object):
    def __init__(self, next_id=None, payload=None):
        """Initialization function for the generic ChainNode object.
        
        Arguments:
            next_id: Reference to the next node in the chain.
            payload: The data for the chain node to encapsulate.
        """
        self.next_id = next_id
        self.payload = payload

def main():
    print('hello, chain')
    
    # TEST AREA - WEAR A HARDHAT
    c = Chain()
    c.add('hello')
    c.add('world')
    c.add('evan')
    c.add('sneath')
    print(c.find_all())
    # END TEST AREA
    
    return

if __name__ == '__main__':
    main()