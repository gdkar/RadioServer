#include <portaudio.h>
#include <stdio.h>

#define SAMPLE_RATE 	(44100)
#define NUM_SECONDS	(8)
#define TABLE_SIZE	(200)

static int patestCallback( const void *inputBuffer, void *outputBuffer, unsigned long framesPerBuffer, const PaStreamCallbackTimeInfo* timeInfo, PaStreamCallbackFlags statusFlags, void *userData );

int main(void );

typedef struct
{

	float left_phase;
	float right_phase;
}
paTestData;

static paTestData data;

int main(){
	PaError err;
	PaStream *stream;
	
	err = Pa_Initialize();
	if (err !=paNoError ) goto error;

	err = Pa_OpenDefaultStream( &stream, 0, 16, paFloat32, SAMPLE_RATE, 256, patestCallback, &data);
	if (err != paNoError) goto error;

	err = Pa_StartStream( stream );

	Pa_Sleep(NUM_SECONDS*1000);

	err=Pa_StopStream( stream );
	if (err != paNoError ) goto error;
	err = Pa_CloseStream( stream );
	if (err != paNoError ) goto error;
	
	err = Pa_Terminate();
	if (err !=paNoError ) goto error;
	return 0;
	error:
		printf("PortAudio error: %s\n", Pa_GetErrorText( err ) );
		return 1;
}
static int patestCallback( const void *inputBuffer, void *outputBuffer, unsigned long framesPerBuffer, const PaStreamCallbackTimeInfo* timeInfo, PaStreamCallbackFlags statusFlags, void *userData )
{
	paTestData *data = (paTestData*)userData;
	
	float *out = (float*)outputBuffer;
	
	unsigned int i;
	unsigned int j;
	(void) inputBuffer;

	for( i=0; i<framesPerBuffer; i++ )
	{
		*out++ = data->left_phase;
		*out++ = data->right_phase;
		out+=14;
		data->left_phase += 0.01f;
		if ( data->left_phase >=1.0f ) data->left_phase -=2.0f;
		
		data->right_phase +=0.03f;
		if ( data->right_phase >=1.0f ) data->right_phase -= 2.0f;
	}
	return 0;
}
