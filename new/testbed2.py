#!/usr/bin/python

from RadioServer import *
import Queue
import time

class Repeater(Listener):
	def __init__(self,inp,out):
		Listener.__init__(self)
		self.inp=inp
		self.out=out
	
	def bound(self):
		self.inq=InputSampler(self.rs)
		self.outq=OutputSampler(self.rs)
		self.rs.subscribeToInput(self.inp,self.inq)
		self.rs.subscribeToOutput(self.out,self.outq)

	def run(self):
		self.i=0
		while self.running:
			try:
				if self.i%1000==0:
					print self.i
				self.i+=1
				samp=self.inq.pop(True,0.1)
				self.outq.push(samp)
				time.sleep(0)
			except Queue.Empty:
				pass

	def stop(self):
		self.rs.outputDevice.flush()
		Listener.stop(self)

rs=RadioServer()
rs.registerDevices()
rs.registerOutput(0,'left')
rs.registerOutput(1,'right')
rs.registerInput(0,'left')
rs.registerInput(1,'right')

r=Repeater('right','right')
l=Repeater('left','left')
rs.addListener(r)
rs.addListener(l)

rs.run_forever()

