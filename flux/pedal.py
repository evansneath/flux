import serial
from PySide import QtCore

class PedalThread(QtCore.QThread):    
    left_clicked = QtCore.Signal()
    right_clicked = QtCore.Signal()
    action_clicked = QtCore.Signal()
    
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
            if line == 'L':
                self.left_clicked.emit()
            elif line == 'R':
                self.right_clicked.emit()
            elif line == 'E':
                self.action_clicked.emit()
