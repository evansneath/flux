#!/usr/bin/python2.7

"""run.py
    This module is the main running module for the Flux Core application.
    The purpose of the module is to combine the Core object class along
    with the Communicator class in order to run ChucK shreds based on the
    incoming Stomp commands. Core may also issue some commands back to
    Stomp. All commands should be included in the cmd_list function and
    from there should act appropriately. The main function should loop
    forever unless a shutdown sequence occurs.
"""

# Library imports
import os
import sys
import traceback
import argparse
import logging

# Core library imports
from effects import Core
from communicator import Communicator


def main():
    """The primary, infinitely running module which handles and serves the
       Arduino control requests as well as executing signal processing accordingly.
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

    # Initialize Core class object
    try:
        logging.debug('Creating Core object')
        core = Core()
        logging.debug('Core object created')
    except:
        logging.error('Fatal error upon Core object creation. Ending now')
        return 1

    # Initialize Communicator class object
    try:
        logging.debug('Creating Communicator object')
        comm = Communicator()
        logging.debug('Communicator object created')
    except:
        logging.error('Fatal error upon Communicator object creation. '
                      'Ending now')
        return 1

    # Begin Core loop initialization function
    try:
        logging.debug('Beginning initialization function')
        init(core, comm)
        logging.debug('Initialization complete')
    except:
        logging.error('Fatal error occured during system initialization. '
                      'Ending now')
        return 1

    # Begin serial command processing loop
    try:
        logging.info('Now handling serial commands...')
        loop(core, comm)
    except:
        logging.error('Fatal error occured during serial communications loop. '
                      'Ending now')
        return 1

    logging.info('Command processing terminated gracefully. Goodbye')
    return 0

def init(core_obj, comm_obj):
    """Initialization function for the main loop"""
    ready = False

    # Get core_obj pickled data from previous sessions
    try:
        logging.debug('Populating Core with saved data')
        #TODO(evan): populate core object with pickled data
        logging.debug('Core object persistant data successfully populated')
    except:
        # This is not a critical error, but send a warning
        logging.warning('No existing data found. Data will need to be '
                        'inputted manually')

    # Establish connection with Arduino device over serial
    try:
        logging.debug('Establishing connection with Arduino')
        comm_obj.connect()
        logging.debug('Connection successfully established')
    except:
        logging.error('Could not connect to Arduino device. '
                      'None found on host system. Ending now')
        raise
    
    return

def loop(core_obj, comm_obj):
    """The continuous, main loop which serves Stomp and
       controls the execution of ChucK shreds.
    """
    #TODO(evan):
    # 1. Populate all possible control sequences from arduino
    # 2. Determine how the program will react to the commands
    while 1:
        # Read next message
        logging.debug('Waiting on new incoming control message')
        #control, value = comm_obj.read()
        # (comm_reader function)

        logging.debug('Control message received. Reacting to message')
        # Act on message contents (reactor function)
        #decision(control, value)

        return # **temporary**

# This module will always be main unless unit testing is taking place.
if __name__ == '__main__':
    sys.exit(main())
