import sys

import effects

#Use PyQt API 2
import sip
sip.setapi('QString', 2)
from PyQt4 import QtCore, QtGui, QtMultimedia

class AudioPath(QtCore.QObject):
    def __init__(self, app):
        super(AudioPath, self).__init__()
        
        info = QtMultimedia.QAudioDeviceInfo.defaultInputDevice()
        format = info.preferredFormat()
        format.setSampleSize(16)
        format.setSampleRate(44100)
        
        if not info.isFormatSupported(format):
            print 'Format not supported, using nearest available'
            format = nearestFormat(format)
            if format.sampleSize != 16:
                #this is important, since effects assume this sample size.
                raise RuntimeError('16-bit sample size not supported!')
        
        self.audio_input = QtMultimedia.QAudioInput(format, app)
        self.audio_output = QtMultimedia.QAudioOutput(format)
        
        self.source = None
        self.sink = None
        
        self.effects = []
        
    def start(self):
        self.source = self.audio_input.start()
        self.sink = self.audio_output.start()
        
        self.source.readyRead.connect(self.on_ready_read)
        
    def stop(self):
        self.audio_input.stop()
        #self.source.readyRead.disconnect(self.on_ready_read)
        self.audio_output.stop()
        
    def on_ready_read(self):
        data = self.source.readAll()
        
        for effect in self.effects:
            effect.process_data(data)
        
        self.sink.write(data)
      
if __name__ == '__main__':  
    app = QtGui.QApplication(sys.argv)
    
    gain = effects.Gain()
    
    path = AudioPath(app)
    path.effects.append(gain)
    
    window = QtGui.QWidget()
    layout = QtGui.QGridLayout()
    window.setLayout(layout)
    
    label = QtGui.QLabel("Gain Test")
    layout.addWidget(label, 1, 0, alignment=QtCore.Qt.AlignHCenter)
    
    slider = QtGui.QSlider()
    slider.setTickPosition(QtGui.QSlider.TicksBothSides)
    slider.setMinimum(1)
    slider.setMaximum(10)
    slider.setTickInterval(1)
    slider.setValue(2)
    
    def on_slider_value_changed(value):
        gain.amount = value

    slider.valueChanged.connect(on_slider_value_changed)
    layout.addWidget(slider, 2, 0, alignment=QtCore.Qt.AlignHCenter)
    play_btn = QtGui.QPushButton("Start")
    play_btn.clicked.connect(path.start)
    layout.addWidget(play_btn, 3, 0, alignment=QtCore.Qt.AlignHCenter)
    
    stop_btn = QtGui.QPushButton("Stop")
    stop_btn.clicked.connect(path.stop)
    layout.addWidget(stop_btn, 4, 0, QtCore.Qt.AlignHCenter)
    
    window.show()
    
    path.start()
    app.exec_()
