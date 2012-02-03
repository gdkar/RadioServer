import pyaudio
import AudioUtils
import math
import time
pa=pyaudio.PyAudio()

def proc(s,t):
	data=AudioUtils.deinterleave(s,2)
	shorts=[AudioUtils.toShorts(k) for k in data]
	shorts[0]=list(shorts[0])
	shorts[1]=list(shorts[1])
	for i in range(len(shorts[0])):
		shorts[0][i]=math.sin(t/(math.pi*10000))*shorts[0][i]
		shorts[1][i]=math.cos(t/(math.pi*10000))*shorts[1][i]

	strings=[AudioUtils.toBytes(k) for k in shorts]
	return AudioUtils.interleave(strings,2)
i=pa.open(rate=44100,channels=2,frames_per_buffer=44100,format=pyaudio.paInt16,input=True)
o=pa.open(rate=44100,channels=2,frames_per_buffer=44100,format=pyaudio.paInt16,output=True)

i.stop_stream()
o.stop_stream()

i.start_stream()
o.start_stream()
t=0
for k in range(2048):
	d=i.read(1024)
	t+=1024
	o.write(proc(d,t))


