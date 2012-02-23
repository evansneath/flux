import sys
import time
import collections
import json
import os

try:
    import pedal
except ImportError:
    pass

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
            
    def widget_index(self, widget):
        return [item.widget() for item in self.itemList].index(widget)

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
    widgets_changed = QtCore.Signal()
    
    _drag_indicator_offset = QtCore.QPoint(0, 13)
    
    def __init__(self):
        super(FluxCentralWidget, self).__init__()
        
        self.drag_widget = None
        
        self.drag_indicator = QtGui.QLabel(self)
        self.drag_indicator.setPixmap(QtGui.QPixmap('res/icons/drag_indicator.png'))
        self.drag_indicator.hide()
        
        self.setAcceptDrops(True)
        
        self.add_tab_button = QtGui.QPushButton(QtGui.QIcon('res/icons/tab_add.png'), '')
        self.add_tab_button.clicked.connect(self.add_tab)
        self.add_tab_button.setObjectName('add_tab_button')
        
        self.setCornerWidget(self.add_tab_button, QtCore.Qt.BottomRightCorner)
        
        self.tabCloseRequested.connect(self.remove_tab)
        self.currentChanged.connect(self.current_changed_event)
        
        self.add_tab()
        
    def current_changed_event(self, index):
        if index >= 0:
            self.widgets_changed.emit()
    
    def add_tab(self, title=None):
        tab = QtGui.QWidget()
        tab.layout = FlowLayout(self, 5)
        tab.setLayout(tab.layout)
        
        if title is None:
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
                
                
    def current_tab_text(self):
        return self.tabText(self.currentIndex())
    
    def rename_tab(self, text=None):
        if self.count():
            if text is None:
                text, ok = QtGui.QInputDialog.getText(self, 'Rename preset', 'Name:',
                                    QtGui.QLineEdit.Normal, self.tabText(self.currentIndex()))
                if ok and text:
                    self.setTabText(self.currentIndex(), text)
            else:
                self.setTabText(self.currentIndex(), text)
                
    def add_widget(self, widget):
        if self.count():
            self.currentWidget().layout.addWidget(widget)
            self.widgets_changed.emit()
        else:
            print "Warning: can't add widget if there are no tabs"
            
    def move_widget(self, index, new_index):
        l = self.currentWidget().layout.itemList
        widget = l.pop(index)
        l.insert(new_index, widget)
        self.currentWidget().layout.invalidate()
        self.widgets_changed.emit()
        
    def remove_widget(self, widget):
        if self.count():
            self.currentWidget().layout.removeWidget(widget)
            widget.hide()
            self.widgets_changed.emit()
        else:
            print "Warning: can't remove widget if there are no tabs"
            
    def _effect_widget_at(self, pos):
        widget = self.childAt(pos)
        
        if type(widget) is QtGui.QWidget:
            #if pos is between two widgets, return the widget to the right if there is one
            margin = self.currentWidget().layout.spacing() * 2
            widget = self.childAt(pos + QtCore.QPoint(margin, 0))
           
        #widget might be a descendant of an EffectWidget, so walk up the ownership tree
        for _ in xrange(5):
            if widget is None:
                return None
            if isinstance(widget, EffectWidget):
                return widget
            else:
                widget = widget.parentWidget()
        return None
        
    def mousePressEvent(self, event):
        widget = self._effect_widget_at(event.pos())
        if widget is not None:
            self.drag_widget = widget
            
            pixmap = QtGui.QPixmap.grabWidget(widget)
            
            mime_data = QtCore.QMimeData()
            mime_data.setData('application/effect_widget', '')
            drag = QtGui.QDrag(self)
            drag.setPixmap(pixmap)
            drag.setMimeData(mime_data)
            drag.start(QtCore.Qt.MoveAction)
        
    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat('application/effect_widget'):
            event.accept()
        else:
            event.ignore()
            
    def dragLeaveEvent(self, event):
        self.drag_indicator.hide()
                
    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat('application/effect_widget'):
            widget = self._effect_widget_at(event.pos())
            if widget is None:
                #place the indicator to the right of the last widget
                widget = self.currentWidget().layout.itemList[-1].widget()
                pos = widget.pos() + self._drag_indicator_offset + QtCore.QPoint(widget.width(), 0)
            else:
                pos = widget.pos() + self._drag_indicator_offset
            
            self.drag_indicator.move(pos)
            self.drag_indicator.show()
            
            event.accept()
        else:
            event.ignore()
            
    def dropEvent(self, event):
        layout = self.currentWidget().layout
        original_index = layout.widget_index(self.drag_widget)
        widget = self._effect_widget_at(event.pos())
        if widget is not None:
            new_index = layout.widget_index(widget)
        else:
            new_index = layout.count()
            
        self.drag_indicator.hide()
        self.move_widget(original_index, new_index)
        
        event.setDropAction(QtCore.Qt.MoveAction)
        event.accept()
        self.drag_widget = None
            
        
class EffectWidgetTitleBar(QtGui.QFrame):
    def __init__(self, title):
        super(EffectWidgetTitleBar, self).__init__()
        self.layout = QtGui.QHBoxLayout()
        self.setLayout(self.layout)
        
        self.label = QtGui.QLabel(title, parent=self)
        self.layout.addWidget(self.label, alignment=QtCore.Qt.AlignLeft)
        
        style = app.style()
        close_icon = QtGui.QIcon('res/icons/tab_close.png')
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
            
            if isinstance(param, effects.DiscreteParameter):
                slider = self._create_discrete_slider(param)
            else:
                slider = self._create_param_slider(param)
            self.layout.addWidget(slider, 3, column, QtCore.Qt.AlignHCenter)
            
            if isinstance(param, effects.TempoParameter):
                button = QtGui.QPushButton('use bpm')
                button.setObjectName('use_bpm_button')
                button.setCheckable(True)
                button.toggled.connect(param.set_use_bpm)
                self.layout.addWidget(button, 4, column, QtCore.Qt.AlignHCenter)
                
    def _create_discrete_slider(self, param):
        widget = QtGui.QWidget()
        layout = QtGui.QGridLayout()
        widget.setLayout(layout)
        
        slider = QtGui.QSlider(self)
        slider.setMinimum(0)
        slider.setMaximum(len(param.choices_dict) - 1)
        slider.setValue(param.choices_dict.keys().index(param.value))
        slider.setTickPosition(QtGui.QSlider.TicksRight)
        slider.setTickInterval(1)
        slider.setOrientation(QtCore.Qt.Vertical)
        slider.valueChanged.connect(self._create_discrete_slot(param))
        slider.setInvertedAppearance(True)
        
        layout.addWidget(slider, 0, 0, len(param.choices_dict), 1, QtCore.Qt.AlignHCenter)
        
        for row, name in enumerate(param.choices_dict):
            label = QtGui.QLabel()
            if param.choices_dict[name]:
                label.setPixmap(QtGui.QPixmap(param.choices_dict[name]))
            else:
                label.setText(name)
                
            if row < len(param.choices_dict) / 3:
                align = QtCore.Qt.AlignTop
            elif row < len(param.choices_dict) * 2 / 3:
                align = QtCore.Qt.AlignHCenter
            else:
                align = QtCore.Qt.AlignBottom
            layout.addWidget(label, row, 1, align)
        
        return widget
                
    def _create_param_slider(self, param):
        slider = QtGui.QSlider(self)
        slider.setMinimum(0)
        slider.setMaximum(EffectWidget._slider_max)
        slider.setValue((float(param.value) / param.maximum) * self._slider_max)
        slider.setTickInterval(10)
        slider.setTickPosition(QtGui.QSlider.TicksBothSides)
        slider.setOrientation(QtCore.Qt.Vertical)
        slider.valueChanged.connect(self._create_slider_slot(param))
        slider.setInvertedAppearance(param.inverted)
        
        return slider
            
    def _create_slider_slot(self, param):
        def update_paramater(value):
            ratio = value / EffectWidget._slider_max
            param.value = param.type(ratio * (param.maximum - param.minimum) + param.minimum)
        return update_paramater
    
    def _create_discrete_slot(self, param):
        def update_paramater(value):
            param.value = param.choices_dict.keys()[value]
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
        #self.button.clicked.connect(self.update_tempo)
        
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
        
        self.setWindowTitle('Flux Audio Effects')
        
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
        
        self.toolbar.addAction(QtGui.QIcon('res/icons/control_play.png'), 'Play', self.play_btn_event)
        self.toolbar.addAction(QtGui.QIcon('res/icons/control_pause.png'), 'Bypass Effects', self.pause_btn_event)
        self.toolbar.addAction(QtGui.QIcon('res/icons/control_stop.png'), 'Stop', self.stop_btn_event)
        self.toolbar.addSeparator()
        self.toolbar.addAction(QtGui.QIcon('res/icons/save.png'), 'Save', self.save_effects)
        self.toolbar.addAction(QtGui.QIcon('res/icons/open.png'), 'Open', self.load_effects)
        self.toolbar.addSeparator()
        self.toolbar.addAction(QtGui.QIcon('res/icons/tab_left.png'), 'Next Preset', self.tab_left_event)
        self.toolbar.addAction(QtGui.QIcon('res/icons/tab_right.png'), 'Previous Preset', self.tab_right_event)
        self.toolbar.addAction(QtGui.QIcon('res/icons/tab_edit.png'), 'Rename Preset', self.rename_tab_event)
        self.toolbar.addSeparator()
        self.toolbar.addWidget(self.tempo_widget)
        self.toolbar.addAction(QtGui.QIcon('res/icons/time_go.png'), 'Tap Tempo', self.tempo_widget.update_tempo)
        
        self.addToolBar(self.toolbar)
        
        #create the central widget
        self.central_widget = FluxCentralWidget()
        self.central_widget.setMovable(True)
        self.central_widget.setTabsClosable (True)
        self.setCentralWidget(self.central_widget)
        self.central_widget.widgets_changed.connect(self.update_audio_path)
        
    def sizeHint(self):
        return QtCore.QSize(600, 400)

    def play_btn_event(self):
        self.audio_path.start()
        
    def pause_btn_event(self):
        self.audio_path.processing_enabled = False
        
    def stop_btn_event(self):
        self.audio_path.stop()
        
    def add_tab_event(self):
        self.central_widget.add_tab()
        
    def tab_left_event(self):
        self.central_widget.select_prev_tab()
    
    def tab_right_event(self):
        self.central_widget.select_next_tab()
        
    def rename_tab_event(self):
        self.central_widget.rename_tab()
        
    def effect_list_item_selected(self, list_item):
        self.add_effect(list_item.text())
            
    def add_effect(self, name, param_values={}):
        """Add an effect widget by name.
        
        Parameters:
            name         -- the name of the effect to add
            param_values -- optional dictionary of parameter names to values that
                            will override the default values
        """
        for effect_class in effects.available_effects:
            if effect_class.name == name:
                effect = effect_class()
                for param, value in param_values.iteritems():
                    try:
                        effect.parameters[param].value = value
                    except KeyError:
                        print 'Error:', name, 'has no parameter', param
                
                self.audio_path.effects.append(effect)
                widget = EffectWidget(effect)
                self.central_widget.add_widget(widget)
                widget.title_bar.exit_btn.clicked.connect(lambda: self.remove_effect_widget(widget))
                return widget
            
    def remove_effect_widget(self, widget):
        try:
            self.audio_path.effects.remove(widget.effect)
        except ValueError as err:
            print 'Info: effect already removed'
        self.central_widget.remove_widget(widget)
            
    def update_audio_path(self):
        panel = self.central_widget.currentWidget()
        self.audio_path.effects = [i.widget().effect for i in panel.layout.itemList]
        
    def save_effects(self):
        effects = [(effect.name, {name:param.value for name, param in effect.parameters.iteritems()}) for effect in self.audio_path.effects]
        
        file_name, file_ext = QtGui.QFileDialog.getSaveFileName(self, 'Save File', self.central_widget.current_tab_text(), 'Effect Save File (*.fxs)')
        
        if file_name:
            with open(file_name, 'w') as f:
                json.dump(effects, f)
        
    def load_effects(self):
        file_names, file_types = QtGui.QFileDialog.getOpenFileNames(self, 'Open Files', filter='Effect Save File (*.fxs)')
        
        for file_name in file_names:
            name, ext = os.path.splitext(os.path.split(file_name)[1])
            if ext == '.fxs':
                self.central_widget.add_tab(name)
                with open(file_name) as f:
                    for effect_name, parameters in json.load(f):
                        effect = self.add_effect(effect_name, parameters)

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    window = FluxWindow(app)
    
    try:
        pedal_thread = PedalThread()
        pedal_thread.left_clicked.connect(window.tab_left_event)
        pedal_thread.right_clicked.connect(window.tab_right_event)
        pedal_thread.action_clicked.connect(window.tab_right_event)
        pedal_thread.start()
    except NameError:
        #pedal wasn't imported correctly
        pass
    window.show()
    app.exec_()
