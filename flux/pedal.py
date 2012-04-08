import serial
import time
from PySide import QtCore

class PedalThread(QtCore.QThread):    
    left_clicked = QtCore.Signal()
    right_clicked = QtCore.Signal()
    action_clicked = QtCore.Signal()
    action_longpress = QtCore.Signal()
    
    def __init__(self):
        super(PedalThread, self).__init__()
        for i in range(256):
            try:
                self.connection = serial.Serial(i, 9600, timeout=1)
            except serial.SerialException:
                pass
        
    def run(self):
        while True: 
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
