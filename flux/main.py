import sys
import time
import collections

import numpy
from PySide import QtCore, QtGui, QtMultimedia

import effects

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
        
        
class FluxCentralWidget(QtGui.QTabWidget):
    def __init__(self):
        super(FluxCentralWidget, self).__init__()
        
        #self.setDocumentMode(True)
        
        self.add_tab_button = QtGui.QPushButton(QtGui.QIcon('res/icons/tab_add.png'), '')
        self.add_tab_button.pressed.connect(self.add_tab)
        self.add_tab_button.setObjectName('add_tab_button')
        
        self.setCornerWidget(self.add_tab_button, QtCore.Qt.BottomRightCorner)
        
        self.tabCloseRequested.connect(self.remove_tab)
        
        self.add_tab()
    
    def add_tab(self):
        tab = QtGui.QWidget()
        tab.layout = FlowLayout(self, 5)
        tab.setLayout(tab.layout)
        
        title = 'Preset %i' % (self.count() + 1)
        self.addTab(tab, title)
        self.setCurrentIndex(self.count() - 1)
        
    def remove_tab(self, index):
        self.removeTab(index)
        if self.count() == 0:
            self.add_tab()
            
    def select_next_tab(self):
        if self.count():
            self.setCurrentIndex((self.currentIndex() + 1) % self.count())
            
    def select_prev_tab(self):
        if self.count():
            if self.currentIndex() > 0:
                self.setCurrentIndex((self.currentIndex() - 1))
            else:
                self.setCurrentIndex(self.count() - 1)
                
    def rename_tab(self):
        print self.count()
        if self.count():
            text, ok = QtGui.QInputDialog.getText(self, 'Rename preset', 'Name:',
                                QtGui.QLineEdit.Normal, self.tabText(self.currentIndex()))
            if ok and text:
                self.setTabText(self.currentIndex(), text)
        
    def add_widget(self, widget):
        if self.count():
            self.currentWidget().layout.addWidget(widget)
        else:
            print "Warning: can't add widget if there are no tabs"
        
    def remove_widget(self, widget):
        if self.count():
            self.currentWidget().layout.removeWidget(widget)
        else:
            print "Warning: can't remove widget if there are no tabs"
            
        
class EffectWidgetTitleBar(QtGui.QFrame):
    def __init__(self, title):
        super(EffectWidgetTitleBar, self).__init__()
        self.layout = QtGui.QHBoxLayout()
        self.setLayout(self.layout)
        
        self.label = QtGui.QLabel(title, parent=self)
        self.layout.addWidget(self.label, alignment=QtCore.Qt.AlignLeft)
        
        style = app.style()
        close_icon = QtGui.QIcon('res/icons/tab_close_hover.png')
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
            slider.setInvertedAppearance(param.inverted)
            self.layout.addWidget(slider, 3, column, QtCore.Qt.AlignHCenter)
            
            if isinstance(param, effects.TempoParameter):
                button = QtGui.QPushButton('use bpm')
                button.setObjectName('use_bpm_button')
                button.setCheckable(True)
                button.toggled.connect(param.set_use_bpm)
                self.layout.addWidget(button, 4, column, QtCore.Qt.AlignHCenter)
            
    def create_slider_slot(self, param):
        def update_paramater(value):
            ratio = value / EffectWidget._slider_max
            param.value = param.type(ratio * (param.maximum - param.minimum) + param.minimum)
        return update_paramater
   
class TempoWidget(QtGui.QWidget):
    def __init__(self):
        super(TempoWidget, self).__init__()
        
        self.setObjectName('tempo_widget')
        
        self.layout = QtGui.QHBoxLayout()
        self.setLayout(self.layout)
        
        self.icon = QtGui.QLabel()
        self.icon.setPixmap(QtGui.QPixmap('res/icons/tempo_text.png'))
        self.layout.addWidget(self.icon)
        
        self.bpm_entry = QtGui.QLineEdit()
        self.bpm_entry.setMaxLength(3)
        self.bpm_entry.setValidator(QtGui.QIntValidator(1, 999, self.bpm_entry))
        self.layout.addWidget(self.bpm_entry)
        
        #self.button = QtGui.QPushButton(QtGui.QIcon('res/icons/time_go.png'), '')
        #self.layout.addWidget(self.button)
        #self.button.pressed.connect(self.update_tempo)
        
        self.tempo_times = collections.deque(maxlen=5)
        
    def update_tempo(self):
        t = time.clock()
        
        #clear the times if it's been 3 seconds
        if self.tempo_times and t - self.tempo_times[-1] > 3:
            self.tempo_times.clear()
            
        self.tempo_times.append(t)
        
        if len(self.tempo_times) >= 2:
            it = iter(self.tempo_times)
            prev = it.next()
            s = 0
            for elem in it:
                s += elem - prev
                prev = elem
            interval = s / float(len(self.tempo_times) - 1)
            self.bpm_entry.setText(str(int(60/interval))) #60/(s per beat) = bpm
        
        
                
class FluxWindow(QtGui.QMainWindow):
    def __init__(self, app):
        super(FluxWindow, self).__init__()
        
        self.app = app
        self.audio_path = effects.AudioPath(app)
        
        with open('res/stylesheet.qss') as style_sheet:
            self.setStyleSheet(style_sheet.read())
            
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
        
        self.tempo_widget = TempoWidget()
        
        #create the top toolbar
        self.toolbar = QtGui.QToolBar()
        self.toolbar.setFloatable(False)
        self.toolbar.setMovable(False)
        
        self.toolbar.addAction(QtGui.QIcon('res/icons/control_play.png'), 'Play', self.play_btn_action)
        self.toolbar.addAction(QtGui.QIcon('res/icons/control_pause.png'), 'Bypass Effects', self.pause_btn_action)
        self.toolbar.addAction(QtGui.QIcon('res/icons/control_stop.png'), 'Stop', self.stop_btn_action)
        self.toolbar.addSeparator()
        self.toolbar.addAction(QtGui.QIcon('res/icons/tab_left.png'), 'Next Preset', self.tab_left_action)
        self.toolbar.addAction(QtGui.QIcon('res/icons/tab_right.png'), 'Previous Preset', self.tab_right_action)
        self.toolbar.addAction(QtGui.QIcon('res/icons/tab_edit.png'), 'Rename Preset', self.rename_tab_action)
        self.toolbar.addSeparator()
        self.toolbar.addWidget(self.tempo_widget)
        self.toolbar.addAction(QtGui.QIcon('res/icons/time_go.png'), 'Tap Tempo', self.tempo_widget.update_tempo)
        
        self.addToolBar(self.toolbar)
        
        #create the central widget
        self.central_widget = FluxCentralWidget()
        self.central_widget.setMovable(True)
        self.central_widget.setTabsClosable (True)
        self.setCentralWidget(self.central_widget)
        self.central_widget.currentChanged.connect(self.update_audio_path)
        
    def sizeHint(self):
        return QtCore.QSize(600, 400)

    def play_btn_action(self):
        self.audio_path.start()
        
    def pause_btn_action(self):
        self.audio_path.processing_enabled = False
        
    def stop_btn_action(self):
        self.audio_path.stop()
        
    def add_tab_action(self):
        self.central_widget.add_tab()
        
    def tab_left_action(self):
        self.central_widget.select_prev_tab()
    
    def tab_right_action(self):
        self.central_widget.select_next_tab()
        
    def rename_tab_action(self):
        self.central_widget.rename_tab()
        
    def effect_list_item_selected(self, list_item):
        for effect_class in effects.available_effects:
            if effect_class.name == list_item.text():
                effect = effect_class()
                self.audio_path.effects.append(effect)
                widget = EffectWidget(effect)
                self.central_widget.add_widget(widget)
                widget.title_bar.exit_btn.pressed.connect(lambda: self.remove_effect_widget(widget))
                return
            
    def remove_effect_widget(self, widget):
        self.central_widget.remove_widget(widget)
        widget.hide()
        try:
            self.audio_path.effects.remove(widget.effect)
        except ValueError as err:
            print 'Info: effect already removed'
            
    def update_audio_path(self, index):
        if index >= 0:
            panel = self.central_widget.currentWidget()
            self.audio_path.effects = [i.widget().effect for i in panel.layout.itemList]
        
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    window = FluxWindow(app)
    window.show()
    app.exec_()
