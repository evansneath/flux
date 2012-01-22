import sys
import time

import numpy
from PySide import QtCore, QtGui, QtMultimedia

import effects

class AudioPath(QtCore.QObject):
    #ts = [] #for performance timing
    def __init__(self, app):
        super(AudioPath, self).__init__()
        
        info = QtMultimedia.QAudioDeviceInfo.defaultInputDevice()
        format = info.preferredFormat()
        format.setChannels(1)
        format.setChannelCount(1)
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
        self.audio_output.stop()
        
    def on_ready_read(self):
        #cast the input data as int32 while it's being processed so that it doesn't get clipped prematurely
        data = numpy.fromstring(self.source.readAll(), 'int16').astype(int)
        
        #t1 = time.clock() #for performance timing
        
        for effect in self.effects:
            if len(data): #empty arrays cause a crash
                data = effect.process_data(data)
                
        ###
        ##performance timing
        #t2 = time.clock() 
        #self.ts.append(t2-t1)
        #if len(self.ts) % 100 == 0:
        #    print sum(self.ts) / float(len(self.ts)) * 1000000, 'us'
        #    self.ts = []
        ###
        
        self.sink.write(data.clip(effects.SAMPLE_MIN, effects.SAMPLE_MAX).astype('int16').tostring())

class FlowLayout(QtGui.QLayout):
    """Flow layout taken from http://developer.qt.nokia.com/doc/qt-4.8/layouts-flowlayout.html"""
    def __init__(self, parent=None, margin=0, spacing=-1):
        super(FlowLayout, self).__init__(parent)

        if parent is not None:
            self.setContentsMargins(margin, margin, margin, margin)

        self.setSpacing(spacing)

        self.itemList = []

    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)

    def addItem(self, item):
        self.itemList.append(item)

    def count(self):
        return len(self.itemList)

    def itemAt(self, index):
        if index >= 0 and index < len(self.itemList):
            return self.itemList[index]

        return None

    def takeAt(self, index):
        if index >= 0 and index < len(self.itemList):
            return self.itemList.pop(index)

        return None

    def expandingDirections(self):
        return QtCore.Qt.Orientations(QtCore.Qt.Orientation(0))

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        height = self.doLayout(QtCore.QRect(0, 0, width, 0), True)
        return height

    def setGeometry(self, rect):
        super(FlowLayout, self).setGeometry(rect)
        self.doLayout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QtCore.QSize()

        for item in self.itemList:
            size = size.expandedTo(item.minimumSize())

        margins = self.getContentsMargins()
        size += QtCore.QSize(margins[0] + margins[2], margins[1] + margins[3])
        return size

    def doLayout(self, rect, testOnly):
        x = rect.x()
        y = rect.y()
        lineHeight = 0

        for item in self.itemList:
            wid = item.widget()
            spaceX = self.spacing() + wid.style().layoutSpacing(QtGui.QSizePolicy.PushButton, QtGui.QSizePolicy.PushButton, QtCore.Qt.Horizontal)
            spaceY = self.spacing() + wid.style().layoutSpacing(QtGui.QSizePolicy.PushButton, QtGui.QSizePolicy.PushButton, QtCore.Qt.Vertical)
            nextX = x + item.sizeHint().width() + spaceX
            if nextX - spaceX > rect.right() and lineHeight > 0:
                x = rect.x()
                y = y + lineHeight + spaceY
                nextX = x + item.sizeHint().width() + spaceX
                lineHeight = 0

            if not testOnly:
                item.setGeometry(QtCore.QRect(QtCore.QPoint(x, y), item.sizeHint()))

            x = nextX
            lineHeight = max(lineHeight, item.sizeHint().height())

        return y + lineHeight - rect.y()
        
class FluxCentralWidget(QtGui.QWidget):
    def __init__(self):
        super(FluxCentralWidget, self).__init__()
        
        self.layout = FlowLayout(self, 5)
        self.setLayout(self.layout)
        
class EffectWidgetTitleBar(QtGui.QFrame):
    def __init__(self, title):
        super(EffectWidgetTitleBar, self).__init__()
        self.layout = QtGui.QHBoxLayout()
        self.setLayout(self.layout)
        
        self.label = QtGui.QLabel(title, parent=self)
        self.layout.addWidget(self.label, alignment=QtCore.Qt.AlignLeft)
        
        style = app.style()
        close_icon = style.standardIcon(QtGui.QStyle.SP_TitleBarCloseButton)
        self.exit_btn = QtGui.QPushButton(close_icon, '')
        self.exit_btn.setObjectName('effect_exit_btn')
        self.exit_btn.setFlat(True)
        self.layout.addWidget(self.exit_btn, alignment=QtCore.Qt.AlignRight)
        
class EffectWidget(QtGui.QFrame):
    _slider_max = 99.0
    def __init__(self, effect):
        super(EffectWidget, self).__init__()
        self.effect = effect
        
        self.setObjectName('effect_frame')
        self.layout = QtGui.QGridLayout()
        self.setLayout(self.layout)
        
        self.title_bar = EffectWidgetTitleBar(effect.name)
        self.title_bar.setObjectName('effect_titlebar')
        self.layout.addWidget(self.title_bar, 0, 0, max((1, len(self.effect.parameters)-1)), 0)
        
        
        for column, (name, param) in enumerate(self.effect.parameters.iteritems()):
            label = QtGui.QLabel(name, self)
            self.layout.addWidget(label, 2, column, QtCore.Qt.AlignHCenter)
            
            slider = QtGui.QSlider(self)
            slider.setMinimum(0)
            slider.setMaximum(EffectWidget._slider_max)
            slider.setValue((float(param.value) / param.maximum) * self._slider_max)
            slider.setTickInterval(10)
            slider.setTickPosition(QtGui.QSlider.TicksBothSides)
            slider.setOrientation(QtCore.Qt.Vertical)
            slider.valueChanged.connect(self.create_slider_slot(param))
            self.layout.addWidget(slider, 3, column, QtCore.Qt.AlignHCenter)
            
    def create_slider_slot(self, param):
        def update_paramater(value):
            ratio = value / EffectWidget._slider_max
            param.value = param.type(ratio * (param.maximum - param.minimum) + param.minimum)
        return update_paramater
    
                
class FluxWindow(QtGui.QMainWindow):
    style_sheet = '''
        #effect_titlebar {
            margin:-8px;
        }
        #effect_titlebar QLabel {
            font-weight:bold;
        }
        #effect_frame {
            border-style:outset;
            border-width:1px;
            border-color:gray;
            border-radius:8px;
            padding:-6px;
            background:qlineargradient(x1:.4, y1:0, x2:.5, y2:1,
                stop:0 transparent, stop:0.2 #dddddd, stop:1 transparent);
        }
        #effect_exit_btn {
            max-width:1.2em;
            max-height:1.2em;
            text-align:center;
        }
    '''
    def __init__(self, app):
        super(FluxWindow, self).__init__()
        
        self.app = app
        self.audio_path = AudioPath(app)
        
        self.setStyleSheet(self.style_sheet)
        #create a dock widget and populate it with available effects
        self.effect_dock = QtGui.QDockWidget('Available Effects')
        self.effect_list = QtGui.QListWidget()
        
        for effect in effects.available_effects:
            item = QtGui.QListWidgetItem(effect.name)
            item.setToolTip(effect.description)
            self.effect_list.addItem(item)
            
        self.effect_list.itemDoubleClicked.connect(self.effect_list_item_selected)
            
        #set the default size for the sidebar
        self.effect_list.sizeHint = lambda: QtCore.QSize(125, 250)
        self.effect_dock.setWidget(self.effect_list)
        self.effect_dock.setFeatures(QtGui.QDockWidget.DockWidgetMovable|QtGui.QDockWidget.DockWidgetFloatable)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.effect_dock)
        
        #create the top toolbar
        style = app.style()
        self.toolbar = QtGui.QToolBar()
        self.toolbar.setFloatable(False)
        self.toolbar.setMovable(False)
        
        play_icon = style.standardIcon(QtGui.QStyle.SP_MediaPlay)
        self.toolbar.addAction(play_icon, 'Play', self.play_btn_action)
        
        pause_icon = style.standardIcon(QtGui.QStyle.SP_MediaPause)
        self.toolbar.addAction(pause_icon, 'Pause', self.pause_btn_action)
        
        self.addToolBar(self.toolbar)
        
        #create the central widget
        self.central_widget = FluxCentralWidget()
        self.setCentralWidget(self.central_widget)
        
    def sizeHint(self):
        return QtCore.QSize(600, 400)

    def play_btn_action(self):
        self.audio_path.start()
        
    def pause_btn_action(self):
        self.audio_path.stop()
        
    def effect_list_item_selected(self, list_item):
        for effect_class in effects.available_effects:
            if effect_class.name == list_item.text():
                effect = effect_class()
                self.audio_path.effects.append(effect)
                widget = EffectWidget(effect)
                self.central_widget.layout.addWidget(widget)
                widget.title_bar.exit_btn.pressed.connect(lambda: self.remove_effect_widget(widget))
                return
            
    def remove_effect_widget(self, widget):
        self.central_widget.layout.removeWidget(widget)
        widget.hide()
        try:
            self.audio_path.effects.remove(widget.effect)
        except ValueError as err:
            print 'Info: effect already removed'
        
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    window = FluxWindow(app)
    window.show()
    app.exec_()
