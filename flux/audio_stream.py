import sys
import math
import time
from PyQt4 import QtCore, QtMultimedia

class AudioStream(object):
    def __init__(self,
                 format,
                 parent=None,
                 input_device=QtMultimedia.QAudioDeviceInfo.defaultInputDevice(),
                 output_device=QtMultimedia.QAudioDeviceInfo.defaultOutputDevice()):
        super(AudioStream, self).__init__()
        
        self.audio_input = QtMultimedia.QAudioInput(input_device, format, parent)
        self.audio_output = QtMultimedia.QAudioOutput(output_device, format, parent)
        self.buffer = QtCore.QBuffer()
        
        #################
        # DEBUGGING INFO
        print 'Input Device:', input_device.deviceName()
        print 'Output Device:', output_device.deviceName()
        # END DEBUGGING
        #################
    
    def start(self):
        self.input_io_data = self.audio_input.start()
        self.input_io_data.readyRead.connect(self._io_data_manipulate)
        self.output_io_data = self.audio_output.start()
    
    def stop(self):
        self.audio_input.stop()
        self.input_io_data.readyRead.disconnect(self._io_data_manipulate)
        self.audio_output.stop()
    
    def _io_data_manipulate(self):
        print 'Running...'
        # read all available input data
        in_data = self.input_io_data.readAll()
        self.buffer.open(QtCore.QIODevice.ReadWrite)
        self.buffer.write(in_data)
        
        # modify buffer data
        byte_array = self.buffer.data()
        modified_byte_array = self.gain(byte_array, 2)
        
        # write modified data to output
        bytes_written = self.output_io_data.write(modified_byte_array)
        self.buffer.close()
    
    def gain(self, bytes, gain_factor):
        index = 0
        for byte in bytes.data():
            pass
        return bytes
        

def main():
    app = QtCore.QCoreApplication(sys.argv)
    
    info = QtMultimedia.QAudioDeviceInfo.defaultInputDevice()
    format = info.preferredFormat()
    
    # use 1 channel, 16-bit samples at 44100 samples per second
    DEFAULT_SAMPLE_SIZE = 16
    DEFAULT_SAMPLE_RATE = 44100
    DEFAULT_CHANNELS = 1
    format.setChannels(DEFAULT_CHANNELS)
    format.setChannelCount(DEFAULT_CHANNELS)
    format.setSampleSize(DEFAULT_SAMPLE_SIZE)
    format.setSampleRate(DEFAULT_SAMPLE_RATE)
    
    stream = AudioStream(format, app)
    stream.start()
    
    print 'Playing...'
    app.exec_()

if __name__ == '__main__':
    main()