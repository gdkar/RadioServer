#include "../../../../../../../usr/include/stdlib.h"
#include "../../../../../../../usr/include/string.h"
#include "../../../../../../../usr/include/unistd.h"
#include "../../../../../../../usr/include/stdio.h"

#include "../../../../../../../usr/src/linux-headers-3.0.0-14/include/sound/jack.h"

const double PI = 3.14;

/*Our output port*/
jack_port_t *output_port;

typedef jack_default_audio_sample_t sample_t;

/*The current sample rate*/
jack_nframes_t sr;

/*one cycle of our sound*/
sample_t* cycle;
/*samples in cycle*/
jack_nframes_t samincy;
/*the current offset*/
long offset=0;

/*frequency of our sound*/
int tone=262;

int process (jack_nframes_t nframes, void *arg){
  /*grab our output buffer*/
  sample_t *out = (sample_t *) jack_port_get_buffer 
                               (output_port, nframes);

  /*CODE GOES HERE!*/
				   
  return 0;      
}

int srate (jack_nframes_t nframes, void *arg){
  printf ("the sample rate is now %lu/sec\n", nframes);
  sr=nframes;
  return 0;
}

void error (const char *desc){
  fprintf (stderr, "JACK error: %s\n", desc);
}

void jack_shutdown (void *arg){
  exit (1);
}

int main (int argc, char *argv[]){
  jack_client_t *client;
  const char **ports;
  
  if (argc < 2) {
    fprintf (stderr, "usage: jack_simple_client \n");
    return 1;
  }
  
  /* tell the JACK server to call error() whenever it
     experiences an error.  Notice that this callback is
     global to this process, not specific to each client.
     
     This is set here so that it can catch errors in the
     connection process
  */
  jack_set_error_function (error);
  
  /* try to become a client of the JACK server */
  
  if ((client = jack_client_new (argv[1])) == 0) {
    fprintf (stderr, "jack server not running?\n");
    return 1;
  }
  
  /* tell the JACK server to call `process()' whenever
     there is work to be done.
  */
  
  jack_set_process_callback (client, process, 0);
  
  /* tell the JACK server to call `srate()' whenever
     the sample rate of the system changes.
  */
  
  
  jack_set_sample_rate_callback (client, srate, 0);
  
  /* tell the JACK server to call `jack_shutdown()' if
     it ever shuts down, either entirely, or if it
     just decides to stop calling us.
  */
  
  jack_on_shutdown (client, jack_shutdown, 0);
  
  /* display the current sample rate. once the client is activated 
     (see below), you should rely on your own sample rate
     callback (see above) for this value.
  */
  printf ("engine sample rate: %lu\n", jack_get_sample_rate (client));
  

  sr=jack_get_sample_rate (client);
  
  /* create two ports */
  
  
  output_port = jack_port_register (client, "output", 
                     JACK_DEFAULT_AUDIO_TYPE, JackPortIsOutput, 0);


  /*CODE GOES HERE!*/


  /* tell the JACK server that we are ready to roll */
  
  if (jack_activate (client)) {
    fprintf (stderr, "cannot activate client");
    return 1;
  }
  
  /* connect the ports*/
  if ((ports = jack_get_ports (client, NULL, NULL, 
                   JackPortIsPhysical|JackPortIsInput)) == NULL) {
    fprintf(stderr, "Cannot find any physical playback ports\n");
    exit(1);
  }
  
  int i=0;
  while(ports[i]!=NULL){
    if (jack_connect (client, jack_port_name (output_port), ports[i])) {
      fprintf (stderr, "cannot connect output ports\n");
    }
    i++;
  }
  
  free (ports);
  
  /* 3 seconds of bleep is plenty*/
  sleep (3);
  jack_client_close (client);
  free(cycle);

  exit (0);
}
