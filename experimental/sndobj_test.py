#!/usr/bin/env python

"""sndobj_test.py

This is a quick module to test the I/O capabilities of pySndObj
"""

# Library imports
import sndobj
import time

def main():
    in_signal = sndobj.SndRTIO(2, sndobj.SND_INPUT)
    out_signal = sndobj.SndRTIO(2, sndobj.SND_OUTPUT)
    
    snd = sndobj.SndIn(in_signal)
    
    out_signal.SetOutput(1, snd)
    out_signal.SetOutput(2, snd)
   
    # Setup thread object
    thread = sndobj.SndThread()
    
    thread.AddObj(in_signal, sndobj.SNDIO_IN)
    thread.AddObj(out_signal, sndobj.SNDIO_OUT)
    thread.AddObj(snd)
    
    # Begin processing thread. Run for 30 seconds
    print('Start: Test thread')
    thread.ProcOn()
    time.sleep(30)
    thread.ProcOff()
    print('Stop: Test thread')
    
    return

if __name__ == '__main__':
    main()