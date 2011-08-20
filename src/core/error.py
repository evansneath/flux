#!/usr/bin/python2.7

"""error.py
    The error.py module defines all of the error codes
    and exceptions present within the Flux project
"""

# Python library imports

class Error(Exception):
    """Base class for exceptions within the Core system"""
    pass

class UnknownError(Error):
    pass

class MessageError(Error):
    pass

class ConnectionError(MessageError):
    pass