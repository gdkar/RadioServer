#!/usr/bin/python

import pyaudio
import Card
import time
import Queue

pa=pyaudio.PyAudio()
print "Starting..."
i=Card.InputDevice(pa)
o=Card.OutputDevice(pa)
s1=SimpleHandler()
s2=SimpleHandler()
i.subscribe(s1,0)
o.subscribe(s2,0)
i.start()
o.start()
#time.sleep(10)
for y in range(0,3000):
	s=s1.get()
	if int(y/50)%2==0:
		s2.put((0,s))
		print "yes"
	else:
		print "no"
i.stop()
o.flush()
o.stop()
pa.terminate()
