#!/usr/bin/env python

"""phonon_test.py

This is a module to test the I/O capabilities of the PySide.Phonon class
"""

# Library imports
import sys
from PySide import QtCore, QtGui
from PySide.phonon import Phonon

def main():
    app = QtGui.QApplication(sys.argv)
    
    print("Begin Setup")
    media_object = Phonon.MediaObject()
    #audio_in = Phonon.AudioCaptureDevice()
    #audio_in_devices = Phonon.BackendCapabilities.availableAudioCaptureDevices()
    #Phonon.BackendCapabilities.availableAudioEffects()
    #audio_out_devices = Phonon.BackendCapabilities.availableAudioOutputDevices()
    #audio_out = Phonon.AudioOutput(Phonon.MusicCategory)
    print("End Setup")
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()