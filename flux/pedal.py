import serial
from PySide import QtCore

class PedalThread(QtCore.QThread):    
    left_clicked = QtCore.Signal()
    right_clicked = QtCore.Signal()
    action_clicked = QtCore.Signal()
    
    def __init__(self):
        super(PedalThread, self).__init__()
        #for i in range(256):
        try:
            self.connection = serial.Serial('/dev/tty.usbserial-A7006Rfp', 9600, timeout=1)
        except serial.SerialException:
            self.connection = None
        
    def run(self):
        while True and self.connection is not None: 
            line = self.connection.readline().rstrip()
            if line == 'L':
                self.left_clicked.emit()
                print 'L'
            elif line == 'R':
                self.right_clicked.emit()
                print 'R'
            elif line == 'E':
                self.action_clicked.emit()
                print 'E'


        
