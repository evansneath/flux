#!/usr/bin/env python

"""main.py

This module is the main running module for the Flux application.
The purpose of the module is to bind the EffectLibrary object class along with
the SerialProtocol class in order to run effects based on the incoming Stomp
commands.
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
    parser = argparse.ArgumentParser(description='Begins Flux Core command reading and processing')
    parser.add_argument('--debug',
                        action='store_true',
                        help='displays debug information in log file')
    parser.add_argument('--log',
                        metavar='FILENAME',
                        action='store',
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
    except:
        return 1
    
    logging.info('Log started successfully')

    # Initialize EffectLibrary class object
    logging.debug('Starting effect library')
    
    try:
        effect_lib = EffectLibrary()
    except:
        logging.error('Fatal error upon effect library creation. Ending now')
        return 1
    
    logging.debug('Effect library started successfully')

    # Initialize SerialProtocol class object
    logging.debug('Starting serial communication')
    
    try:
        serial = SerialProtocol('/dev/tty.usbserial', 9600)
    except:
        logging.error('Fatal error upon serial communication initialization. '
                      'Ending now')
        return 1
    
    logging.debug('Serial communication started successfully')

    # Begin serial command processing loop
    logging.info('Now handling user operations...')
    
    try:
        # begin processing loop
        pass
    except:
        logging.error('Fatal error occured during serial communications loop. '
                      'Ending now')
        return 1

    logging.info('Command processing terminated gracefully. Goodbye')
    return 0

# This module will always be main unless unit testing is taking place.
if __name__ == '__main__':
    sys.exit(main())