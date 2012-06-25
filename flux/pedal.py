import serial
import time
import platform
from PySide import QtCore

class PedalThread(QtCore.QThread):    
    left_clicked = QtCore.Signal()
    right_clicked = QtCore.Signal()
    action_clicked = QtCore.Signal()
    action_longpress = QtCore.Signal()
    
    # holds serial connection object
    connection = None
    
    # holds default serial connection attributes
    baud = 9600
    timeout = 1
    
    # connection failed flag
    connected = False
    
    def __init__(self):
        super(PedalThread, self).__init__()
        
        os = platform.system()
        
        if os == 'Darwin':            
            try:
                # try to connect to device @ /dev/tty.usbserial if using mac
                self.connection = serial.Serial('/dev/tty.usbserial-A7006Rfp', self.baud, timeout=self.timeout)
                self.connected = True
            except serial.SerialException:
                # not able to connect on os x. fail quietly.
                pass
        elif os == 'Windows':
            for i in range(256):
                try:
                    # for each port, try to connect to the arduino board
                    self.connection = serial.Serial(i, self.baud, timeout=self.timeout)
                    self.connected = True
                except serial.SerialException:
                    # not able to connect on windows. fail quietly.
                    pass
    
    def run(self):
        while True and self.connected: 
            line = self.connection.readline().rstrip()
            if line == 'L1':
                self.left_clicked.emit()
            elif line == 'R1':
                self.right_clicked.emit()
            elif line == 'E1':
                t1 = time.clock()
            elif line == 'E0':
                t2 = time.clock()
                if (t2 - t1) < 2:
                    self.action_clicked.emit()
                elif (t2 - t1) > 2:
                    self.action_longpress.emit()
