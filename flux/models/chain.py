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
    
    def __str__(self):
        """Overrides the string output to provide a well formatted view of
           the chain.
        """
        pass
    
    def _tick(self):
        """Increments the id ticker by one."""
        self.__id_ticker += 1
    
    def _create_node(self, payload):
        """Creates a new node and adds it to the dictionary.
        
        Arguments:
            payload: Data payload to add to the new node.
        Returns:
            The id of the created node.
        """
        node_id = self.__id_ticker
        self.__nodes[node_id] = Node(payload=payload)
        self._tick()
        
        return node_id
    
    def _delete_node(self, node_id):
        """Deletes the node from the dictionary.
        
        Arguments:
            node_id: The id of the node to delete.
        Returns:
            The payload of the deleted node.
        """
        # The payload should be saved to return from the function.
        del_payload = self.__nodes[node_id].payload
        
        # Delete the object to ensure no unreferenced nodes.
        del(self.__nodes[node_id])
        
        return del_payload
    
    def extend_tail(self, payload):
        """Adds a new payload node onto the end of the chain.
        
        Arguments:
            payload: Data payload to add to the newly created node.
        Returns:
            The id of the created tail node.
        """
        # Create new node.
        node_id = self._create_node(payload)
        
        # If the new node is the only, this is the head node as well.
        if self.count == 1:
            self.__head_id = node_id
        else:
            self.__nodes[self.__tail_id].next_ids.append(node_id)
        
        self.__tail_id = node_id
        
        return node_id
    
    def extend_head(self, payload):
        """Adds a new payload node onto the front of the chain.
        
        Arguments:
            payload: Data payload to add to the newly created node.
        Returns:
            The id of the created head node.
        """
        # Create new node.
        node_id = self._create_node(payload)
        
        # If the new node is the only, this is the tail node as well.
        if self.count == 1:
            self.__tail_id = node_id
        else:
            self.__nodes[node_id].next_ids.append(self.__head_id)
        
        self.__head_id = node_id
        
        return node_id
    
    def insert(self, node_id, payload):
        """Adds a new node directly after the specified node in the chain.
        
        Arguments:
            node_id: The node to displace. The new node will be created after
                this node in the list and take the node's next nodes.
            payload: Data payload to add to the newly created node.
        Returns:
            The id of the created node. None on failure.
        """
        if node_id not in self.__nodes:
            # The desired node to replace does not exist
            new_node_id = None
        elif node_id == self.__tail_id:
            new_node_id = self.push_tail(payload)
        else:
            new_node_id = self._create_node(payload)
            self.__nodes[new_node_id].next_ids = self.__nodes[node_id].next_ids
            self.__nodes[node_id].next_ids = [new_node_id]            
        
        return new_node_id
    
    def branch(self, prev_id, next_id, payload):
        pass
    
    def remove(self, node_id):
        """Removes a specified node from the chain.
        
        Arguments:
            node_id: The id of the node to remove from the chain.
        Returns:
            The payload of the removed chain node. None on failure.
        """
        # Determine if the node id inputted exists.
        if not self.__nodes.has_key(node_id):
            return None
        elif len(self.__nodes) == 1:
            # Node is the only existing in the chain
            self.__head_id = None
            self.__tail_id = None
            return self._delete_node(node_id)
        elif node_id == self.__head_id \
            and len(self.__nodes[node_id].next_ids) == 1:
            # Node is head node
            new_head_id = self.__nodes[node_id].next_ids[0]
            self.__head_id = new_head_id
            return self._delete_node(node_id)
        elif node_id == self.__tail_id \
            and len(self._find_by_next_id(node_id)) == 1:
            # Node is tail node
            new_tail_id = self._find_by_next_id(node_id)[0]
            self.__tail_id = new_tail_id
            self.__nodes[new_tail_id].next_ids.remove(node_id)
            return self._delete_node(node_id)
        else:
            # Node is a middle node
            parent_ids = self._find_by_next_id(node_id)
            next_ids = self.__nodes[node_id].next_ids
            if len(parent_ids) == 1 or len(next_ids) == 1:
                # If the node is singularly referenced on one end...
                for parent_id in parent_ids:
                    self.__nodes[parent_id].next_ids.append(self.__nodes[node_id].next_ids)
                    self.__nodes[parent_id].next_ids.remove(node_id)
                return self._delete_node(node_id)
    
    def get_next(self, node_id):
        """Retrieves the specified node's next node.
        
        Arguments:
            node_id: The desired node id.
        Returns:
            The specified node's next nodes. None on failure.
        """
        if self.__nodes.has_key(node_id):
            return self.__nodes[node_id].next_ids
    
    def get_payload(self, node_id):
        """Searches for a specified node id from the chain and returns the
           current payload
        
        Arguments:
            node_id: The id of the node to search for.
        Returns:
            The node payload object if found. None on failure.
        """
        if self.__nodes.has_key(node_id):
            return self.__nodes[node_id].payload
    
    def set_payload(self, node_id, payload):
        """Searches for a speicifed node id from the chain and sets the payload.
        
        Arguments:
            node_id: The id of the node to search for.
            payload: The data object to set as payload for the node.
        Returns:
            True on success. None on failure.
        """
        if self.__nodes.has_key(node_id,):
            self.__nodes[node_id].payload = payload
            return True
    
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
            if node_id in node[1].next_ids:
                found.append(node[0])
        return found
    
    def __get_count(self):
        """Getter for the node count property."""
        return len(self.__nodes)
    
    def __get_head(self):
        """Getter for the chain's head property."""
        return self.__head_id
    
    def __get_tail(self):
        """Getter for the chain's tail property."""
        return self.__tail_id
    
    count = property(fget=__get_count, doc='Gets the chain node count.')
    head = property(fget=__get_head, doc='Gets the chain head.')
    tail = property(fget=__get_tail, doc='Gets the chain tail.')

class Node(object):
    def __init__(self, payload=None):
        """Initialization function for the generic Node object.
        
        Arguments:
            payload: The data for the chain node to encapsulate.
        """
        super(Node, self).__init__()
        self.next_ids = list()
        self.payload = payload

def main():
    print('hello, chain')
    return

if __name__ == '__main__':
    main()