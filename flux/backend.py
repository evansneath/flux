import time

from PySide import QtCore, QtMultimedia
import numpy as np

import effects

class AudioPath(QtCore.QObject):
    """Class that handles audio input and output and applying effects.
    
    Parameters:
    app -- a QApplication or QCoreApplication
    """
    ts = [] #for performance timing
    def __init__(self, app):
        super(AudioPath, self).__init__()
        
        info = QtMultimedia.QAudioDeviceInfo.defaultInputDevice()
        format = info.preferredFormat()
        format.setChannels(effects.CHANNEL_COUNT)
        format.setChannelCount(effects.CHANNEL_COUNT)
        format.setSampleSize(effects.SAMPLE_SIZE)
        format.setSampleRate(effects.SAMPLE_RATE)
        
        if not info.isFormatSupported(format):
            print 'Format not supported, using nearest available'
            format = nearestFormat(format)
            if format.sampleSize != effects.SAMPLE_SIZE:
                #this is important, since effects assume this sample size.
                raise RuntimeError('16-bit sample size not supported!')
        
        self.audio_input = QtMultimedia.QAudioInput(format, app)
        self.audio_input.setBufferSize(effects.BUFFER_SIZE)
        self.audio_output = QtMultimedia.QAudioOutput(format)
        
        self.source = None
        self.sink = None
        
        self.processing_enabled = True
        
        self.effects = []
    
    def start(self):
        self.processing_enabled = True
        
        self.source = self.audio_input.start()
        self.sink = self.audio_output.start()
        
        self.source.readyRead.connect(self.on_ready_read)
    
    def stop(self):
        self.audio_input.stop()
        self.audio_output.stop()
    
    def on_ready_read(self):
        #cast the input data as int32 while it's being processed so that it doesn't get clipped prematurely
        data = np.fromstring(self.source.readAll(), 'int16').astype(float)
        
        if self.processing_enabled:
            #t1 = time.clock() #for performance timing
            
            for effect in self.effects:
                if len(data): #empty arrays cause a crash, use len(data) since np.array doesn't have an implicit boolean value
                    data = effect.process_data(data)
                    
            ####
            ##processing performace timing
            #t2 = time.clock() 
            #self.ts.append(t2-t1)
            #if len(self.ts) % 100 == 0:
            #    print sum(self.ts) / float(len(self.ts)) * 1000000, 'us'
            #    self.ts = []
            ####
            ##time between on_ready_read calls
            #self.ts.append(time.clock())
            #if len(self.ts) % 100 == 0:
            #    print (sum(self.ts[i] - self.ts[i-1] for i in range(1, len(self.ts))) / (len(self.ts) - 1)) * 1000, 'ms'
            #    self.ts = []
            #        
            ###
        
        self.sink.write(data.clip(effects.SAMPLE_MIN, effects.SAMPLE_MAX).astype('int16').tostring())
