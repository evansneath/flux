#!/usr/bin/env python

"""protocol.py

This is the Flux Stomp to Core serial communication manager.
The SerialProtocol class holds the byte-stream communcation
that is read and then parses it into usable commands.
"""

# Library imports
import serial
import logging

class SerialProtocol(serial.Serial):
    """SerialProtocol class

    A communication bridge class for parsing and initiating talk
    between the Arduino device running Stomp and the Core classes.

    Attributes:
        port: The device port which to connect.
        baudrate: The bits per second transfe r rate of the serial connection.
        is_connected: Displays current connection status.
    """
    _IS_MODIFIED_SIZE = 1
    _CONTROL_SIZE = 2
    _VALUE_SIZE = 4

    def protocol_read(self):
        """Reads the incoming serial communcation from the Arduino device
           attached and parses a single message into a 'control' segment
           and a 'value' segment. Each being 8 Bytes.

        Returns:
            control: Incoming message control code.
            value: Incoming message control updated value.
        """
        # Read flag indicating control value change
        in_data = self.read(_IS_MODIFIED_SIZE)
        
        if in_data == True:
            logging.debug('Control modified. Reading new value')
                
            control = self.read(_CONTROL_SIZE)
            value = self.read(_VALUE_SIZE)
                
            logging.debug('New control and value successfully read')
                
            return control, value
        else:
            return None

# Main function for class file
# (should remain relatively unused outside of small-scale class testing)
def main():
    print('hello, communicator')
    return

if __name__ == '__main__':
    main()