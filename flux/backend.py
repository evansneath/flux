import time

from PySide import QtCore, QtMultimedia
import numpy as np

import effects

class AudioPath(QtCore.QObject):
    """Class that handles audio input and output and applying effects.
    
    Parameters:
    app -- a QApplication or QCoreApplication
    """
    
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
        
        self.recording_loop = False
        self.playing_loop = False
        self.interval_size = None
        self.record_track = None
        self.playback_track = None
        
    def start_recording(self):
        self.record_track = np.array([])
        self.recording_loop = True
    
    def stop_recording(self):
        self.recording_loop = False
        self.playback_track = self.record_track
        self.record_track = None
        
    def start_loop_playback(self, bpm=None):
        if self.playback_track is not None:
            self.playing_loop = True
        
    def stop_loop_playback(self):
        self.playing_loop = False
        
    def erase_recorded_data(self):
        self.playing_loop = False
        self.playback_track = None
    
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
        
        #empty arrays cause a crash; use len(data) since np.array doesn't have an implicit boolean value
        if len(data) == 0:
            return
        
        if self.processing_enabled:
            for effect in self.effects:
                data = effect.process_data(data)

        #add the recorded track to the data
        if self.playing_loop and len(data) != 0:
            data += self.playback_track[:len(data)]
            self.playback_track = np.roll(self.playback_track, -len(data))
            
        self.sink.write(data.clip(effects.SAMPLE_MIN, effects.SAMPLE_MAX).astype('int16').tostring())
        
        #record the data it's written to the sink to reduce latency
        if self.recording_loop:
            self.record_track = np.concatenate((self.record_track, data))
