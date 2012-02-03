""" Record a few seconds of audio and save to a WAVE file. """

import pyaudio
import wave
import sys
import time
import struct
import numpy
import math
import EasyDTMF
import DTMFbuffer


chunk = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 8
channel=1
RATE = 44100
RECORD_SECONDS = 1
WAVE_OUTPUT_FILENAME = "output"
WAVE_OUTPUT_FILETYPE="wav"
rec=False
really_write=True
went_silent=0
files_count=0
files_written=[]
DTMF_seen=False
buf=DTMFbuffer.DTMFBuffer()

p = pyaudio.PyAudio()
    
def extract_channels(block,channels):
    count = len(block)/2
    format = "%dh"%(count)
    shorts = struct.unpack( format, block )
    out=[[] for i in range(channels)]
    for i in range(len(shorts)):
        out[i%channels].append(shorts[i])
    return out
stream = p.open(format = FORMAT,
                channels = CHANNELS,
                rate = RATE,
                input = True,
                frames_per_buffer = chunk)

print "* recording"
init_chans=[]
#all=['' for i in range(CHANNELS)]
t=time.time()
out=[]
while time.time()<t+1:
    data=stream.read(chunk)
    chan_data=extract_channels(data,CHANNELS)
    out.extend(chan_data[channel])
print numpy.mean(numpy.abs(out))
m=8*numpy.mean(numpy.abs(out))
t=time.time()
went_silent=time.time()
while time.time()<t+120:
#for i in range(1):
    
    data = stream.read(chunk)
    chan_data=extract_channels(data,CHANNELS)
    out.extend(chan_data[channel])
    buf.update(chan_data[channel][:512],RATE)
    
    if buf.trig():
        if buf.get()[-1]=='5':
            q_delay=time.time()
            while time.time()<q_delay+1.: continue
            play_file=wave.open(files_written[-1],'rb')
            play_stream=p.open(format=p.get_format_from_width(play_file.getsampwidth()),channels=play_file.getnchannels(),rate=play_file.getframerate(),output=True)
            play_data=play_file.readframes(chunk)
            while play_data!='':
                play_stream.write(play_data)
                play_data=play_file.readframes(chunk)
            play_stream.close()
            play_file.close()

    if buf.trig():
        really_write=False
    if numpy.mean(numpy.abs(chan_data[channel]))>m:
        if not rec:
            rec=True
            if len(out)>RATE*.5: out=out[-int(RATE*.5):] 
        went_silent=time.time()
        DTMF_seen=DTMF_seen or buf.trig()
    else:
        if time.time()>went_silent+2 and rec:
            print time.time()-went_silent
            rec=False
            if really_write:
                st=''.join([struct.pack('h',i) for i in out])
                wf=wave.open(WAVE_OUTPUT_FILENAME+str(files_count)+'.'+WAVE_OUTPUT_FILETYPE, 'wb')
                files_written.append(WAVE_OUTPUT_FILENAME+str(files_count)+'.'+WAVE_OUTPUT_FILETYPE)
                wf.setnchannels(1)
                wf.setsampwidth(p.get_sample_size(FORMAT))
                wf.setframerate(RATE)
                wf.writeframes(st)
                wf.close()
            really_write=True
            files_count+=1
    #for i in range(len(all)):
    #    chan_data[i]
    #    all[i]+=''.join([struct.pack('h',chan_data[i][j]) for j in range(len(chan_data[i]))])
    
print "* done recording"

stream.close()
p.terminate()

# write data to WAVE file
#data = all[1]
#print type(data)
#wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
#wf.setnchannels(1)
#wf.setsampwidth(p.get_sample_size(FORMAT))
#wf.setframerate(RATE)
#wf.writeframes(data)
#wf.close()

