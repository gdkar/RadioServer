import threading
import pyaudio
import Queue
import time
import struct

class InputDevice:
	# Defaults
	FORMAT=pyaudio.paInt16
	RATE=44100
	CHANNELS=2
	CHUNKSIZE=1024

	def __init__(self,pa,format=FORMAT,rate=RATE,channels=CHANNELS,chunksize=CHUNKSIZE):
		self.pa=pa
		self.format=format
		self.rate=rate
		self.channels=channels
		self.chunksize=chunksize

		self.inputBuffer=Queue.Queue()
		self.subscribers=[[] for i in range(channels)] # necessary due to references

		self.rlt=ReadLoopThread(self)
		self.ipt=InputProcessingThread(self)

	def subscribe(self,who,channel):
		self.subscribers[channel].append(who)

	def start(self):
		self.rlt.start()
		self.ipt.start()

	def stop(self):
		self.rlt.stop()
		self.ipt.stop()

	def deinterleave(self,chunk):
		bytes_per_sample=2
		format_string=str(self.chunksize*self.channels)+'h'
		array=struct.unpack(format_string,chunk)
		split=[array[i::self.channels] for i in range(self.channels)]
		return split

class InputProcessingThread(threading.Thread):
	def __init__(self,id):
		threading.Thread.__init__(self)
		self.id=id

	def stop(self):
		self.go=False
		self.join()

	def start(self):
		self.go=True
		threading.Thread.start(self)

	def run(self):
		self.process=False
		while self.go:
			#print "IPT OK"
			try:
				chunk=self.id.inputBuffer.get(True,.1)
				split_samples=self.id.deinterleave(chunk)
				for chan_num in range(self.id.channels):
					for subscriber in self.id.subscribers[chan_num]:
						subscriber.put(split_samples[chan_num],False)
			except Queue.Empty:
				pass

class ReadLoopThread(threading.Thread):
	def __init__(self,id):
		self.id=id
		threading.Thread.__init__(self)
		self.stream=id.pa.open(format=id.format,rate=id.rate,channels=id.channels,input=True,frames_per_buffer=id.chunksize)

	def stop(self):
		self.go=False
		self.join()
		self.stream.close()

	def start(self):
		self.go=True
		threading.Thread.start(self)

	def run(self):
		while self.go:
			self.id.inputBuffer.put(self.stream.read(self.id.chunksize),False)
			time.sleep(0) # Yield. Ensures the next bit is executed entirely within one time quantum. A hack. Increases stability greatly.

class OutputDevice:
	# Defaults
	FORMAT=pyaudio.paInt16
	RATE=44100
	CHANNELS=2
	CHUNKSIZE=1024

	QSIZE=20
	QSTART=10

	def __init__(self,pa,format=FORMAT,rate=RATE,channels=CHANNELS,chunksize=CHUNKSIZE,qsize=QSIZE,qstart=QSTART):
		self.pa=pa
		self.format=format
		self.rate=rate
		self.channels=channels
		self.chunksize=chunksize

		self.qsize=qsize
		self.qstart=qstart

		self.outputBuffer=Queue.Queue(self.qsize)

		self.subscribers=[[] for i in range(channels)] # necessary due to references

		self.wlt=WriteLoopThread(self)
		self.opt=OutputProcessingThread(self)

	def start(self):
		self.wlt.start()
		self.opt.start()

	def stop(self):
		self.opt.stop()
		self.wlt.stop()

	def subscribe(self,who,channel):
		self.subscribers[channel].append(who)

	def interleave(self,array):
		bytes_per_sample=2
		joined=[array[chan][samp] for samp in range(self.chunksize) for chan in range(self.channels)] 
		format_string=str(self.chunksize*self.channels)+'h'
		chunk=struct.pack(format_string,*joined)
		return chunk

	def flush(self):
		self.wlt.flush()
		self.opt.flush()

class OutputProcessingThread(threading.Thread):
	def __init__(self,od):
		threading.Thread.__init__(self)
		self.od=od
		self.quiet=[0]*od.chunksize
		self.doFlush=False

	def stop(self):
		self.go=False
		self.join()

	def start(self):
		self.go=True
		threading.Thread.start(self)

	def flush(self):
		self.doFlush=True

	def run(self):
		while self.go or self.doFlush:
			#print "OPT OK"
			all_chans=[]
			found=False
			for chan_num in range(self.od.channels):
				samples=self.quiet
				for subscriber in self.od.subscribers[chan_num]:
					if not subscriber.empty():
						(priority,samples)=subscriber.get()
						found=True
						break
				all_chans.append(samples)
			if found:
				chunk=self.od.interleave(all_chans)
				self.od.outputBuffer.put(chunk)
			else:
				time.sleep(.1)
				self.doFlush=False

class WriteLoopThread(threading.Thread):
	def __init__(self,od):
		self.od=od
		threading.Thread.__init__(self)
		self.stream=od.pa.open(format=od.format,rate=od.rate,channels=od.channels,output=True,frames_per_buffer=od.chunksize)
		self.doFlush=False
		self.quiet='\0'*self.od.CHUNKSIZE*self.od.CHANNELS*2

	def stop(self):
		self.go=False
		self.join()
		self.stream.close()

	def start(self):
		self.go=True
		threading.Thread.start(self)

	def flush(self):
		self.doFlush=True

	def run(self):
		self.process=False
		while self.go or self.doFlush or self.od.opt.doFlush:
			#print "WLT OK"

			q=self.od.outputBuffer.qsize()
			if q>self.od.qstart:
				self.process=True
			elif q<1:
				self.process=False

			if self.process:
				chunk=self.od.outputBuffer.get()
			else:
				if not self.od.opt.doFlush:
					self.doFlush=False
				chunk=self.quiet
			self.stream.write(chunk,self.od.chunksize)

