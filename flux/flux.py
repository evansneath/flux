#!/usr/bin/env python

"""flux.py

This module is the main running module for the Flux application.
"""

# Library imports
import sys
import argparse
import logging

def main():
    """The primary, infinitely running module which handles and serves the
       Arduino control requests as well as executing signal processing
       accordingly.
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Begins Flux command reading and processing.')
    parser.add_argument('--debug',
                        action='store_true',
                        help='Displays debug information in log file.')
    parser.add_argument('--log',
                        metavar='FILENAME',
                        action='store',
                        default=None,
                        help='Specifies filename of the log file.')
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
    
    logging.info('Log started successfully.')

    # Begin processing loop
    logging.info('Now handling user operations...')
    
    try:
        pass
    except:
        logging.error('Fatal error occured during processing loop. '
                      'Ending now.')
        return 1

    logging.info('Processing terminated gracefully. Goodbye.')
    return 0

# This module will always be main unless unit testing is taking place.
if __name__ == '__main__':
    sys.exit(main())