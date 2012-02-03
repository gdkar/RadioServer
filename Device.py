import threading
import pyaudio
import Queue
import Channel
import AudioUtils
class InputDevice(threading.Thread):
	def __init__(self,pa):
		threading.Thread.__init__(self)
		self.streamInfo={'FORMAT':pyaudio.paInt16,'RATE':44100,'CHUNK':1024,'CHANNELS':2}
		self.stream=pa.open(format=self.streamInfo['FORMAT'],rate=self.streamInfo['RATE'],channels=self.streamInfo['CHANNELS'],input=True,frames_per_buffer=self.streamInfo['CHUNK'])
		self.chans=[Channel.Channel()]*self.streamInfo['CHANNELS']
		self.running=True
	def run(self):
		while self.running:
			chunk=self.stream.read(self.streamInfo['CHUNK'])
			data=AudioUtils.deinterleave(chunk,self.streamInfo['CHANNELS'])
		self.stream.close()
	def attachInput(self,index):
		return self.chans[index].attachOutput()
	def stop(self):
		self.running=False

class OutputDevice(threading.Thread):
	def  __init__(self,pa):
		threading.Thread.__init__(self)
		self.streamInfo={'FORMAT':pyaudio.paInt16,'RATE':44100,'CHUNK':1024,'CHANNELS':2}
		self.stream=pa.open(format=self.streamInfo['FORMAT'],rate=self.streamInfo['RATE'],channels=self.streamInfo['CHANNELS'],output=True,frames_per_buffer=self.streamInfo['CHUNK'])
		self.chans=[Channel.Channel()]*self.streamInfo['CHANNELS']
		[c.seek(0) for c in self.chans]
		self.running=True
	def run(self):
		while self.running:
			delay=max([c.qsize() for c in self.chans])
			if delay>self.streamInfo['CHUNK']*2:
				chunk=[c.read(min(self.streamInfo['CHUNK']),c.qsize()) for c in self.chans]
				for i in range(len(chunk)):
					if len(chunk[i])<self.streamInfo['CHUNK']:
						chunk[i]+='\0'*(self.streamInfo['CHUNK']-len(chunk[i]))
				data=AudioUtils.interleave(chunk,self.streamInfo['CHANNELS'])
				self.stream.write(data)
	def attachOutput(self,index):
		return self.chans[index].attachInput()
	def stop(self):
		self.running=False
