import Channel
import threading


class Listener(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		running=True
		self.rs=None
		self.inputStreams={}
		self.outputStreams={}

	def addInput(self,name):
		self.inputStreams[name]=self.rs.addInputDeviceByName(name)
		self.inputSreams[name].seek(0)

	def addOutput(self,name):
		self.outputStreams[name]=self.rs.addOutputDevicesByName(name)
		self.inputStreams[name].seek(0)

	def run(self):
		while running:
			pass
	
	def stop(self):
		self.running=False
