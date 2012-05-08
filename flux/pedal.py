import serial
import time
import platform
from PySide import QtCore

class PedalThread(QtCore.QThread):    
    left_clicked = QtCore.Signal()
    right_clicked = QtCore.Signal()
    action_clicked = QtCore.Signal()
    action_longpress = QtCore.Signal()
    
    def __init__(self):
        super(PedalThread, self).__init__()
        baud = 9600
        connect_fail = False
        
        if platform.system == 'Darwin':
            try:
                # try to connect to device @ /dev/tty.usbserial if using mac
                self.connection = serial.Serial('/dev/tty.usbserial', baud, timeout=1)
            except serial.SerialException:
                # not able to connect on Mac, trying alternate approach next
                connect_fail = True
        
        if platform.system == 'Windows' or connect_fail == True:
            for i in range(256):
                try:
                    # for each port, try to connect to the arduino board
                    self.connection = serial.Serial(i, baud, timeout=1)
                    connect_fail = False
                except serial.SerialException:
                    connect_fail = True
    
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
