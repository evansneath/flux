from PyQt4 import QtMultimedia
from struct import *

# packs wave file header into binary data based on audio input device qualities
def packWaveHeader(format):
    if not format.isValid():
        # not a valid format to pack
        return None
    
    # configure RIFF chunk
    riff_chunk_id = 'RIFF'
    riff_chunk_data_size = 4 # riff chunk size
    riff_type = 'WAVE' # specify wave format
    
    # configure format chunk
    fmt_chunk_id = 'fmt'
    fmt_chunk_data_size = 16 # fmt chunk size
    
    if format.codec() == "audio/pcm":
        fmt_compression_code = 1 # pcm audio compression code
    else:
        fmt_compression_code = 0 # unknown codec

    fmt_channels = format.channelCount()
    fmt_sample_rate = format.sampleRate()
    fmt_extra_format_bytes = 0
    fmt_significant_bits_per_sample = 16
    fmt_block_align = fmt_significant_bits_per_sample / 8 * fmt_channels
    fmt_average_bytes_per_second = fmt_sample_rate * fmt_block_align
    
    # set byte order formatting
    byte_order = format.byteOrder()
    if byte_order == QtMultimedia.QAudioFormat.BigEndian:
        pack_format_str = '>'
    elif byte_order == QtMultimedia.QAudioFormat.LittleEndian:
        pack_format_str = '<'
    
    pack_format_str += '4sL4s3sLHHLLHH'
    
    # pack info into wave file header and return
    return pack(pack_format_str, riff_chunk_id, riff_chunk_data_size,
                riff_type, fmt_chunk_id, fmt_chunk_data_size,
                fmt_compression_code, fmt_channels, fmt_sample_rate,
                fmt_average_bytes_per_second, fmt_block_align,
                fmt_significant_bits_per_sample)


# input device specs checking method (disposable) 
def printInputDeviceSpecifications():
    default_input_device = QtMultimedia.QAudioDeviceInfo(QtMultimedia.QAudioDeviceInfo.defaultInputDevice())
    print "--- Default Input Device Specifications ---"
    print "Supported Channel Counts:", default_input_device.supportedChannelCounts()
    print "Supported Channels:", default_input_device.supportedChannels()
    supported_codec_list = default_input_device.supportedCodecs()
    for codec in supported_codec_list:
        print "Supported Codecs:", codec
    print "Supported Frequencies:", default_input_device.supportedFrequencies()
    print "Supported Sample Rates:", default_input_device.supportedSampleRates()
    print "Supported Sample Sizes:", default_input_device.supportedSampleSizes()
    print "Supported Sample Type:", default_input_device.supportedSampleTypes()

    return


# format checking method (disposable)
def printInputFormat(format):
    print "-- Default Input Device Format ---"
    # detect if little or big endian
    if format.byteOrder() == QtMultimedia.QAudioFormat.BigEndian:
        print "Byte Order: Big Endian"
    elif format.byteOrder() == QtMultimedia.QAudioFormat.LittleEndian:
        print "Byte Order: Little Endian"
    
    print "Channel Count:", format.channelCount()
    print "Channels:", format.channels()
    print "Codec:", format.codec()
    print "Frequency:", format.frequency()
    print "Sample Rate:", format.sampleRate()
    print "Sample Size:", format.sampleSize()
    print "Sample Type:", format.sampleType()
    print "Byte Order:", format.byteOrder()
    
    print "Vaid Format:", format.isValid()

    return


def main():
    # this is the tester function for the wave file header packing method
    info = QtMultimedia.QAudioDeviceInfo()
    
    # check system devices for input
    print "--- Available Input Devices ---"
    input_device_list = info.availableDevices(QtMultimedia.QAudio.AudioInput)
    for input_device in input_device_list:
        print input_device.deviceName()
    
    # use default input device for this test
    default_input_device = QtMultimedia.QAudioDeviceInfo(QtMultimedia.QAudioDeviceInfo.defaultInputDevice())
    
    # get the preferred format of the default input device
    format = default_input_device.preferredFormat()
    
    # change some settings for a one channel setup (MONO)
    format.setChannelCount(1)
    format.setChannels(1)

    # pack and print the wave file header
    packed = packWaveHeader(format)
    
    byte_order = format.byteOrder()
    if byte_order == QtMultimedia.QAudioFormat.BigEndian:
        fmt = '>'
    elif byte_order == QtMultimedia.QAudioFormat.LittleEndian:
        fmt = '<'
    fmt += '4sL4s3sLHHLLHH'
    
    unpacked = unpack(fmt, packed)
    
    print "--- Wave Header File Generation ---"
    print "Packed:", packed
    print "Unpacked:", unpacked
    
    return


if __name__ == '__main__':
    main()