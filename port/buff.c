#ifdef __cplusplus
extern "C"
{
#endif /* __cplusplus */

#include <portaudio.h>
#include <stdio.h>

struct{
	long	index;
	long	bufferSize;
	char*	buffer;
}ringBuffer;
typedef struct ringBuffer Ringbuffer;
struct{
	int 		index;
	RingBuffer*	buffer;
}readPort;
typedef struct readPort ReadPort;
long RingBuffer_Init(RingBuffer * rbuf, long NumBytes, void *dataPtr){
	rbuf->bufferSize=NumBytes;
	buffer=(char*)dataPtr;
	memset(buffer,0,NumBytes);
	index=0;
	return 0;
}
long RingBuffer_Write(RingBuffer * rbuf, long NumBytes, void* data){
	long length1,length2;
	if(NumBytes> rbuf->bufferSize){NumBytes=rbuf->BufferSize;}
	if(NumBytes+rbuf->index<rbuf->bufferSize){
		memcpy(rbuf->buffer[rbuf->index],data,NumBytes);
	}
	else{
		length1=rbuf->bufferSize-rbuf->index;
		length2=NumBytes-length1;
		memcpy(rbuf->buffer[rbuf->index],data,length1);
		data=((char*)data)+length1;
		memcpy(rbuf->buffer,data,length2);
	}
	rbuf->index=rbuf->(index+NumBytes)%rbuf->bufferSize;
	return NumBytes;
}

long RingBuffer_AddReader(RingBuffer* rbuf, ReadPort* rp){
	rp->buffer = rbuf;
	rp->index = rbuf->index;
	return 0;
}

long RingBuffer_Read(ReadPort* rp, long NumBytes, void* data){
	long length1,length2;
	void* data1,buffer1;
	bytesAvailable=(rp->buffer->index-rp->index);
	if(bytesAvailable>=0){
		if(NumBytes<byteAvailable){NumBytess=BytesAvailable;}
		memcpy(data,rp->buffer->buffer,NumBytes);
	}else{
		length1=rp->buffer->bufferSize-rp->index;
		length2=NumBytes-length1;
		if(length2>rp->buffer->index){
			length2=rp->buffer->index;
			NumBytes=length1+length2;
		}
		data1=((char*)data)+length1;
		buffer1=(rp->buffer->buffer)+rp->index;
		memcpy(data,buffer1,length1);
		memcpy(data1,rp->buffer->buffer,length2);
	}

	return NumBytes;
}


#ifdef __cplusplus
}
#endif /* __cplusplus */
