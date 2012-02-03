from Card import *
from pyaudio import PyAudio
import threading
import signal

class RadioServer:
	def __init__(self):
		self.pa=PyAudio()
		self.input_names={}
		self.output_names={}
		self.listeners=[]

	def registerDevices(self,inputDevice=None,outputDevice=None):
		if inputDevice==None:
			self.inputDevice=InputDevice(self.pa)
		else:
			self.inputDevice=inputDevice

		if outputDevice==None:
			self.outputDevice=OutputDevice(self.pa)
		else:
			self.outputDevice=outputDevice



	def registerInput(self,descriptor,name):
		self.input_names[name]=descriptor

	def registerOutput(self,descriptor,name):
		self.output_names[name]=descriptor

	def subscribeToInput(self,name,queue):
		self.inputDevice.subscribe(queue,self.input_names[name])

	def subscribeToOutput(self,name,queue):
		self.outputDevice.subscribe(queue,self.output_names[name])

	def addListener(self,listener):
		self.listeners.append(listener)
		listener.bind(self)

	def start(self):
		for l in self.listeners:
			l.start()
		self.inputDevice.start()
		self.outputDevice.start()

	def stop(self):
		self.inputDevice.stop()
		self.outputDevice.stop()
		for l in self.listeners:
			l.stop()
		self.pa.terminate()

	def sigint(self,signal,frame):
		self.stop()

	def run_forever(self):
		self.start()
		signal.signal(signal.SIGINT,lambda s,f:self.sigint(s,f))
		signal.pause()

class Listener(threading.Thread):
	def bind(self,server):
		self.rs=server
		self.bound()

	def bound(self):
		pass

	def start(self):
		self.running=True
		threading.Thread.start(self)

	def stop(self):
		self.running=False
		self.join()


class InputSampler(Queue.Queue):
	def __init__(self,rs):
		self.chunk=[]
		self.l=rs.inputDevice.chunksize
		Queue.Queue.__init__(self)

	def size(self):
		return self.qsize()*self.l+len(self.chunk)
	
	def pop(self,block=True,timeout=None):
		if len(self.chunk)==0:
			self.chunk=list(self.get(block,timeout))
			self.chunk.reverse()
		return self.chunk.pop()

class OutputSampler(Queue.Queue):
	def __init__(self,rs):
		self.chunk=[]
		self.l=rs.outputDevice.chunksize
		Queue.Queue.__init__(self)
		self.priority=0

	def push(self,what,block=True,timeout=None):
		self.chunk.append(what)
		if len(self.chunk)==self.l:
			self.send(block,timeout)

	def send(self,block=True,timeout=None):
		self.put((self.priority,tuple(self.chunk)),block,timeout)
		self.chunk=[]

	def flush(self,block=True,timeout=None):
		self.chunk+=[0]*(self.l-len(self.chunk))
		self.send(block,timeout)

