#ifdef __cplusplus
extern "C"
{
#endif /* __cplusplus */

#include <portaudio.h>
#include <stdio.h>
//#include "buff.c"

#define SAMPLE_RATE 		(44100)
#define PA_SAMPLE_TYPE		paFloat32
#define FRAMES_PER_BUFFER	(1024)
#define NUM_SECONDS 		(8)
#define NUM_IN_CHANNELS		(8)
#define NUM_OUT_CHANNELS 	(8)



static int patchCallback( const void *inputBuffer, void *outputBuffer, unsigned long framesPerBuffer, const PaStreamCallbackTimeInfo* timeInfo, PaStreamCallbackFlags statusFlags, void *userData );

int main(void );

typedef struct
{
	int patch[8];
}
patchData;

static patchData data;
static float* sampleBlock0;
static float* sampleBlock1;
static float* ringout;
static float* end;
int main(){
	PaError err;
	PaStream *stream;
	int halfbuf = sizeof(float)*FRAMES_PER_BUFFER * NUM_IN_CHANNELS;
	int buf=2*sizeof(float)*FRAMES_PER_BUFFER*NUM_IN_CHANNELS;;
	sampleBlock0 = (float *) malloc ( 	buf);
	sampleBlock1 = sampleBlock0+(FRAMES_PER_BUFFER*NUM_IN_CHANNELS);
	ringout = (float*) sampleBlock0;
	end = sampleBlock0+(2*FRAMES_PER_BUFFER*NUM_IN_CHANNELS);
	PaStreamParameters inputParameters, outputParameters;
	data.patch[0]=1;
	data.patch[1]=-1;
	data.patch[2]=-1;
	data.patch[3]=-1;
	data.patch[4]=-1;
	data.patch[5]=-1;
	data.patch[6]=-1;
	data.patch[7]=-1;
	
	err = Pa_Initialize();
	if (err !=paNoError ) goto error;

    inputParameters.device = Pa_GetDefaultInputDevice(); /* default input device */
    inputParameters.channelCount = NUM_IN_CHANNELS;       /* stereo input */
    inputParameters.sampleFormat = PA_SAMPLE_TYPE;
    inputParameters.suggestedLatency = Pa_GetDeviceInfo( inputParameters.device )->defaultLowInputLatency;
    inputParameters.hostApiSpecificStreamInfo = NULL;

    outputParameters.device = Pa_GetDefaultOutputDevice(); /* default output device */
    outputParameters.channelCount = NUM_OUT_CHANNELS;       /* stereo output */
    outputParameters.sampleFormat = PA_SAMPLE_TYPE;
    outputParameters.suggestedLatency = Pa_GetDeviceInfo( outputParameters.device )->defaultLowOutputLatency;
    outputParameters.hostApiSpecificStreamInfo = NULL;

    err = Pa_OpenStream(
              &stream,
              &inputParameters,
              &outputParameters,
              SAMPLE_RATE,
              64,
              0, /* paClipOff, */  /* we won't output out of range samples so don't bother clipping them */
              patchCallback,
              NULL );
	if (err != paNoError) goto error;

	err = Pa_StartStream( stream );
	int i = 0;
	for(i=0;i<(NUM_SECONDS*SAMPLE_RATE)/FRAMES_PER_BUFFER; ++i){
	err = Pa_ReadStream( stream,sampleBlock0,FRAMES_PER_BUFFER);
	if (err!=paNoError)goto error;
	err = Pa_ReadStream( stream,sampleBlock1,FRAMES_PER_BUFFER);
	if (err!=paNoError)goto error;
	}

	err=Pa_StopStream( stream );
	if (err != paNoError ) goto error;
	err = Pa_CloseStream( stream );
	if (err != paNoError ) goto error;
	
	free(sampleBlock0);
	err = Pa_Terminate();
	if (err !=paNoError ) goto error;
	return 0;
	error:
		printf("PortAudio error: %s\n", Pa_GetErrorText( err ) );
		return 1;
}
static int patchCallback( const void *inputBuffer, void *outputBuffer, unsigned long framesPerBuffer, const PaStreamCallbackTimeInfo* timeInfo, PaStreamCallbackFlags statusFlags, void *userData )
{
	patchData *data = (patchData*)userData;
	float* output=(float*)outputBuffer;
	float* input=(const float*)inputBuffer;	
	float* out1,*in1;
	unsigned short i;
	unsigned long j;
	//if(inputBuffer==NULL){for (i=0;i<framesPerBuffer*2;i++){*(output++)=0;}}	
	//else{
	/*for(i=0;i<2;i++){
		if(0<=(data->patch)[i]&&(data->patch)[i]<2){
			out1=output+i;
			in1=input+i;
			for(j=0;j<framesPerBuffer;j++) *out1++=*in1++;
			//in1=input+(data->patch)[i];
	//		for(j=0;j<framesPerBuffer;j++){
	//			*out1++=*in1++;
			//}
		}
	//}
	}*/
	for(i=0;i<framesPerBuffer*NUM_OUT_CHANNELS;i++){
		*output++=*ringout++;
		if (ringout>=end){ringout=sampleBlock0;}
	}
	return paContinue;
}

#ifdef __cplusplus
}
#endif /* __cplusplus */
