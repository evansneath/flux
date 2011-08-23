#!/usr/bin/python2.7

"""main.py

This module is the main running module for the Flux Core application.
The purpose of the module is to combine the Core object class along with
the SerialProtocol class in order to run effects based on the incoming Stomp
commands. Core may also issue some commands back to Stomp.
"""

# Library imports
import sys
import argparse
import logging
from effect import EffectLibrary
from protocol import SerialProtocol

def main():
    """The primary, infinitely running module which handles and serves the
       Arduino control requests as well as executing signal processing
       accordingly.
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Begins Flux Core command reading and processing')
    parser.add_argument('--debug', action='store_true',
                        help='displays debug information in log file')
    parser.add_argument('--log', metavar='FILENAME', action='store',
                        default=None,
                        help='specifies filename of the core log file')
    args = parser.parse_args()

    if args.debug:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO

    # Begin logger
    try:
        logging.basicConfig(format='%(levelname)s:%(message)s',
                            filename=args.log, filemode='w', 
                            level=log_level)
        logging.info('Core reactor started')
    except:
        return 1

    # Initialize EffectLibrary class object
    try:
        logging.debug('Starting effect library')
        effect_lib = EffectLibrary()
        logging.debug('Effect library started successfully')
    except:
        logging.error('Fatal error upon effect library creation. Ending now')
        return 1

    # Initialize SerialProtocol class object
    try:
        logging.debug('Starting serial communication')
        serial = SerialProtocol('/dev/tty.usbserial', 9600)
        logging.debug('Serial communication started successfully')
    except:
        logging.error('Fatal error upon serial communication initialization. '
                      'Ending now')
        return 1

    # Begin serial command processing loop
    try:
        logging.info('Now handling user operations...')
        while True:
            return # temporary
    except:
        logging.error('Fatal error occured during serial communications loop. '
                      'Ending now')
        return 1

    logging.info('Command processing terminated gracefully. Goodbye')
    return 0

# This module will always be main unless unit testing is taking place.
if __name__ == '__main__':
    sys.exit(main())