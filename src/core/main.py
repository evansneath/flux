#!/usr/bin/python2.7

"""main.py

This module is the main running module for the Flux Core application.
The purpose of the module is to combine the Core object class along with
the Communicator class in order to run effects based on the incoming Stomp
commands. Core may also issue some commands back to Stomp.
"""

# Library imports
import sys
import argparse
import logging
from effect import EffectLibrary
from communicator import Communicator

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
        logging.debug('Creating effect library')
        effect_lib = EffectLibrary()
        logging.debug('Effect library created')
    except:
        logging.error('Fatal error upon effect library creation. Ending now')
        return 1

    # Initialize Communicator class object
    try:
        logging.debug('Creating communicator object')
        communicator = Communicator()
        logging.debug('Communicator object created')
    except:
        logging.error('Fatal error upon communicator object creation. '
                      'Ending now')
        return 1

    # Begin initialization function
    try:
        logging.debug('Beginning initialization function')
        init(effect_lib, communicator)
        logging.debug('Initialization complete')
    except:
        logging.error('Fatal error occured during system initialization. '
                      'Ending now')
        return 1

    # Begin serial command processing loop
    try:
        logging.info('Now handling user operations...')
        loop(effect_lib, communicator)
    except:
        logging.error('Fatal error occured during serial communications loop. '
                      'Ending now')
        return 1

    logging.info('Command processing terminated gracefully. Goodbye')
    return 0

def init(effect_lib, communicator):
    """Initialization function for the main loop"""
    ready = False

    # Get core_obj pickled data from previous sessions
    try:
        logging.debug('Populating effect library with saved data')
        #TODO(evan): populate core object with pickled data
        logging.debug('Core object persistant data successfully populated')
    except:
        # This is not a critical error, but send a warning
        logging.warning('No existing data found. Data will need to be '
                        'inputted manually')

    # Establish connection with Arduino device over serial
    try:
        logging.debug('Establishing connection with Arduino')
        communicator.connect()
        logging.debug('Connection successfully established')
    except:
        logging.error('Could not connect to Arduino device. '
                      'None found on host system. Ending now')
        raise

    return

def loop(effect_lib, communicator):
    while True:
        return # **temporary**

# This module will always be main unless unit testing is taking place.
if __name__ == '__main__':
    sys.exit(main())