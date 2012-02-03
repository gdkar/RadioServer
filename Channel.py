import io

#import Queue
class Channel(io.BytesIO):
	def attachOutput(self, buffer_size=io.DEFAULT_BUFFER_SIZE):
		return io.BufferedReader(self,buffer_size)
	def attachInput(self,buffer_size=io.DEFAULT_BUFFER_SIZE):
		return io.BufferedWriter(self,buffer_size)
	def qsize(self):
		return len(self.getvalue())
