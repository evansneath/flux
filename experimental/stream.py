from PyQt4 import QtCore, QtGui, QtMultimedia
import struct, collections

class AudioStream(QtCore.QIODevice):
    header = ''
    
    def __init__(self, audio_input_device=None):
        super(AudioStream, self).__init__()
        
        # take header formatting from default input device if no other is given
        if audio_input_device is None:
            audio_input_device = QtMultimedia.QAudioDeviceInfo(
                QtMultimedia.QAudioDeviceInfo.defaultInputDevice())
            
        audio_input_format = audio_input_device.preferredFormat()

        audio_input_format.setChannelCount(1)
        audio_input_format.setChannels(1)
        self.header = self._packWaveHeader(audio_input_format)
        
        self.open(QtCore.QIODevice.ReadWrite|QtCore.QIODevice.Unbuffered)
        self.buffer = collections.deque(self.header)
        
        self.seek_position = 0
    
    def _get(self, maxlen):
        """Concatinate the first maxlen items of the buffer"""
        return ''.join(self.buffer.popleft() for _ in xrange(min(maxlen, len(self.buffer))))
    
    def _packWaveHeader(self, input_device_format):
        if not input_device_format.isValid():
            # not a valid format to pack
            return None
        
        # configure RIFF chunk
        riff_chunk_id = 'RIFF'
        riff_chunk_data_size = 4 # riff chunk size
        riff_type = 'WAVE' # specify wave format
        
        # configure format chunk
        fmt_chunk_id = 'fmt'
        fmt_chunk_data_size = 16 # fmt chunk size
        
        if input_device_format.codec() == "audio/pcm":
            fmt_compression_code = 1 # pcm audio compression code
        else:
            fmt_compression_code = 0 # unknown codec
    
        fmt_channels = input_device_format.channelCount()
        fmt_sample_rate = input_device_format.sampleRate()
        fmt_extra_format_bytes = 0
        fmt_significant_bits_per_sample = 16
        fmt_block_align = fmt_significant_bits_per_sample / 8 * fmt_channels
        fmt_average_bytes_per_second = fmt_sample_rate * fmt_block_align
        
        # set byte order formatting
        byte_order = input_device_format.byteOrder()
        if byte_order == QtMultimedia.QAudioFormat.BigEndian:
            pack_format_str = '>'
        elif byte_order == QtMultimedia.QAudioFormat.LittleEndian:
            pack_format_str = '<'
        
        pack_format_str += '4sL4s3sLHHLLHH'
        
        # pack info into wave file header and return
        return struct.pack(pack_format_str, riff_chunk_id, riff_chunk_data_size,
                    riff_type, fmt_chunk_id, fmt_chunk_data_size,
                    fmt_compression_code, fmt_channels, fmt_sample_rate,
                    fmt_average_bytes_per_second, fmt_block_align,
                    fmt_significant_bits_per_sample)
    
    def read(self, maxlen):
        print 'read', maxlen
        return super(AudioStream, self).read(maxlen)
    
    def readData(self, maxlen):
        print 'readData', maxlen
        if self.seek_position == 0:
            data = self._get(maxlen)
        else:
            #If the seek_offset != 0, we have to return a slice.
            #   The only way to do that on a deque is to use rotations
            self.buffer.rotate(-self.seek_position)
            data = self._get(maxlen)
            self.buffer.extend(data)
            self.buffer.rotate(self.seek_position)
        return data
    
    def writeData(self, data):
        self.buffer.extend(data)
        #print 'writeData', len(data)
        return len(data)
    
    def seek(self, pos):
        print 'seek:', pos
        self.seek_position = pos
        return True
    
    def reset(self):
        print 'reset'
        self.seek_position = 0
        return True
    
    def bytesAvailable(self):
        #call QIODevice.bytesAvailable staticly, because QIODevice has its own buffer
        #print 'bytesAvailable', len(self.buffer)
        return len(self.buffer) + QtCore.QIODevice.bytesAvailable(self)
    
    def size(self):
        print 'size', len(self.buffer)
        return len(self.buffer)
    
    #def atEnd(self):
    #    return self.bytesAvailable() == 0
    
    def isSequential(self):
        return False