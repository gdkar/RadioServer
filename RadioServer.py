import Device
import AudioUtils
import Channel
import Listener
import pyaudio
import io
class RadioServer():
	def __init__(self):
		self.pa=pyaudio.PyAudio()
		self.inputCard=Device.InputDevice(self.pa)
		self.outputCard=Device.OutputDevice(self.pa)
		
		self.inputDevicesByName={}
		self.outputDevicesByName={}
		self.listeners=[]

		self.running=True
		pass

	def addInputDeviceByName(self,name,index):
		self.inputDevicesByName[name]=index
	
	def addOutputDeviceByName(self,name,index):
		self.outputDevicesByName[name]=index

	def connectInputDeviceByName(self,name):
		return self.inputCard.attachInput(self.inputDevicesByName[name])
	def connectOutputDeviceByName(self,name):
		return self.outputCard.attachOutput(self.outputDevicesByName[name])
	
	def bind(self,listener):
		self.listeners.append(listener)
		listener.rs=self
		pass
	def start(self):
		self.run()
	def run(self):
		for listener in self.listeners:
			listener.start()
		self.inputCard.start()
		self.outputCard.start()
		
		o=self.connectInputDeviceByName("right--line in")
		o.seek(0,whence=2)
		while self.running:
			pass

		#we got killed. cleanup.
		for listener in self.listeners:
			listener.stop()
			listener.join()
		self.inputCard.stop()
		self.inputCard.join()
		self.outputCard.stop()
		self.outputCard.join()
		self.pa.terminate()
		pass

	def stop(self):
		self.running=False
