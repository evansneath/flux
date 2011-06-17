#!/usr/bin/python3.2

"""communicator.py
    This is the Flux Stomp to Core serial communication manager.
    Communicator also implements the Message class object contained
    in this module. The ControlProtocol class holds the byte-stream 
    communcation that is read and then parses it into usable commands.
"""

# Python standard library imports
import serial
import logging

class ControlProtocol:
    """ControlProtocol class

    Provides standard serial Stomp-to-Core message protocol
    functions to parse from raw data or assemble a new message.
    """

    # Public functions
    def parse_incoming(raw_bits):
        #TODO(evan): Make this method: bytes --> control, value

        return #control, value

    def build_outgoing(control, value):
        #TODO(evan): Make this method: control, value --> bytes

        return #raw_bits

class Communicator:
    """Communicator class

    A communication bridge class for parsing and initiating talk
    between the Arduino device running Stomp and the Core classes.

    Attributes:
        device: The device port which to connect.
        baudrate: The bits per second transfer rate of the serial connection.
        is_connected: Displays current connection status.
    """

    # Class constants
    __BYTES_PER_MESSAGE = 2

    # Initialization function
    def __init__(self, device=None, baudrate=9600, is_connected=False):
        """Begin Communicator definition"""
        self.__device = device
        self.__baudrate = baudrate
        self.__is_connected = is_connected
        self.__serial = None

    # Private functions
    def __get_device(self):
        """Getter for the Communicator device property"""
        return self.__device

    def __set_device(self, new_device):
        """Setter for the Communicator device property"""
        self.__device = new_device

    def __get_baudrate(self):
        """Getter for the Communicator baudrate property"""
        return self.__baudrate

    def __set_baudrate(self, new_baudrate):
        """Setter for the Communicator baudrate property"""
        self.__baudrate = new_baudrate

    def __get_is_connected(self):
        """Getter for the Communicator is_connected property"""
        return self.__is_connected

    # Property declarations
    device = property(fget=__get_device, fset=__set_device,
                      doc='Gets or sets the serial connection device')
    baudrate = property(fget=__get_baudrate, fset=__set_baudrate,
                        doc='Gets or sets the serial connection baudrate')
    is_connected = property(fget=__get_is_connected,
                            doc='Gets the serial connection status')

    # Public functions
    def connect(self):
        """Creates a serial connection between the object and the device
           port specified with the chosen baudrate

        Arguments:
            device: Location of the device to attempt a serial connection.
            baudrate: The bits per second of information to attempt to 
                     transfer once a connection has been established.
        Returns:
            True on success, False if otherwise.
        """
        self.__is_connected = False

        # Overwrites any current serial connections and creates a new one
        try:
            self.__serial = serial.Serial(port=self.__device, 
                                          baudrate=self.__baudrate)
            self.__is_connected = True
            logging.debug('Serial connection on port {0} '
                          'established'.format(port))
        except serial.serialutil.SerialException as e:
            logging.error('Serial connection failure: {0}'.format(e))
    
        return self.__is_connected

    def disconnect(self):
        """Terminates the current serial connection between object and the
           specified device port.

        Returns:
            True on success, False if otherwise.
        """
        try:
            self.__serial.close()
            self.__is_connected = False
            logging.debug('Serial disconnection successful')
            return True
        except:
            logging.debug('Serial disconnection failure')
            return False

    def read(self):
        """Reads the incoming serial communcation from the Arduino device
           attached and parses a single message into a 'control' segment
           and a 'value' segment. Each being 8 Bytes.

        Returns:
            Control and value objects. None if no connection is present.
        """
        if self.__is_connected:
            logging.debug('Begin control message read')
            in_data = read(__BYTES_PER_MESSAGE)
            control, value = ControlProtocol.parse_incoming(in_data)
            logging.debug('Control message successfully read and parsed')
            return control, value
        else:
            # No serial communication link. Return failure.
            logging.debug('Cannot read control message. '
                          'No connection established')
            return None

    def write(self, control, value):
        """Writes the given control and value in the standard core-to-stomp
           protocol.

        Arguments:
            control: The control which to write to.
            value: The new value of this control.
        Returns:
            True on success, False if otherwise.
        """
        if self.__is_connected:
            logging.debug('Begin control message write')
            out_data = ControlProtocol.build_outgoing(control, value)
            self.__serial.write(out_data)
            logging.debug('Control message successfully built and written')
            return True
        else:
            # No serial communication link. Return failure.
            logging.debug('Cannot write control message. '
                          'No connection established')
            return False


# Main function for class file
# (should remain relatively unused outside of small-scale class testing)
def main():
    print('hello, communicator')
    return

if __name__ == '__main__':
    main()
