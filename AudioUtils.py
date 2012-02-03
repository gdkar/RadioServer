import struct

def interleave(data,channels,bitwidth=2):
	DATA=['']*min(len(data),channels)*len(data[0])
	for i in range(min(len(data),channels)):
		for j in range(bitwidth):
			DATA[i*bitwidth+j::bitwidth*channels]=data[i][j::bitwidth]
	return ''.join(DATA)
	
	
def deinterleave(data,channels,bitwidth=2):
	DATA=[['']*(len(data)/channels) for i in range(channels)]
	for i in range(channels):
		for j in range(bitwidth):
			DATA[i][j::bitwidth]=data[i*bitwidth+j::bitwidth*channels]
	return [''.join(DATA[i]) for i in range(channels)]

def toShorts(data,format='h',bitwidth=2):
	count=len(data)/bitwidth
	compiled_format=str(count)+format
	return struct.unpack(compiled_format,data)
def toBytes(data,format='h',bitwidth=2):
	return ''.join([struct.pack(format,i) for i in data])
