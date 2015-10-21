/* Sample multithreaded program that guards access to a shared buffer
 *   - multiple readers can read in parallel
 *   - single writer can write at a time
 *   - when a writer is blocked by a reader, no new readers are allowed until writer has finished
 *
 * Compile with:
 *    gcc main.c -lpthread -std=c11
 */
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include <string.h>
#include <unistd.h>
#include <stdbool.h>

#define NUM_THREADS  20
#define BUFFER_SIZE 1024

char buffer[ BUFFER_SIZE ];

pthread_mutex_t writer_mutex;
pthread_mutex_t buffer_mutex;
pthread_cond_t cond_writer_done;
pthread_cond_t cond_reader_done;

int num_readers = 0;
bool waiting_writer = false;

void *slow_memcpy( void *dest, const void *src, size_t n )
{
	for( unsigned int i = 0; i < n; i++ ) {
		((char*)dest)[ i ] = ((char*) src)[ i ];
		usleep(100);
	}
	return dest;
}

void thread_safe_read( char *buf, size_t num_bytes, size_t read_offset )
{
	assert( read_offset + num_bytes <= BUFFER_SIZE );

	pthread_mutex_lock( &buffer_mutex );
	while( waiting_writer ) {
		pthread_cond_wait( &cond_writer_done, &buffer_mutex );
	}
	num_readers++;
	pthread_mutex_unlock( &buffer_mutex );

	slow_memcpy( buf, buffer + read_offset, num_bytes );

	pthread_mutex_lock( &buffer_mutex );
	num_readers--;
	if( num_readers == 0 ) {
		pthread_cond_signal( &cond_reader_done );
	}
	pthread_mutex_unlock( &buffer_mutex );
}

void thread_safe_write( char *buf, size_t num_bytes, size_t write_offset )
{
	assert( write_offset + num_bytes <= BUFFER_SIZE );

	pthread_mutex_lock( &writer_mutex );
	pthread_mutex_lock( &buffer_mutex );

	waiting_writer = true;
	while( num_readers > 0 ) {
		pthread_cond_wait( &cond_reader_done, &buffer_mutex );
	}
	waiting_writer = false;

	slow_memcpy( buffer + write_offset, buf, num_bytes );
	pthread_cond_signal( &cond_writer_done );

	pthread_mutex_unlock( &buffer_mutex );
	pthread_mutex_unlock( &writer_mutex );
}

void *worker_thread( void * i )
{
	char local_buf[ BUFFER_SIZE ];
	unsigned int worker_id = (unsigned int) i;

	for( unsigned int i = 0; i < 10; i++ ) {
		thread_safe_read( local_buf, BUFFER_SIZE, 0 );
		printf( "Worker thread number: %u read: %s\n", worker_id, local_buf );

		char *format_str[] = {
			"Hello from thread %u",
			"Greetings from thread %u",
			"Howdy-ho from thread %u",
			"Hi from thread %u",
		};
		snprintf( local_buf, BUFFER_SIZE, format_str[ worker_id % 4 ], worker_id );
		thread_safe_write( local_buf, BUFFER_SIZE, 0 );

		usleep(1000*worker_id);
	}

	return NULL;
}

int main (int argc, char *argv[])
{
	pthread_t threads[ NUM_THREADS ];

	pthread_mutex_init( &writer_mutex, NULL );
	pthread_mutex_init( &buffer_mutex, NULL );
	pthread_cond_init( &cond_writer_done, NULL );
	pthread_cond_init( &cond_reader_done, NULL );

	char buffer_init_value[] = "initial value";
	thread_safe_write( buffer_init_value, sizeof(buffer_init_value), 0 );

	pthread_attr_t attr;
	pthread_attr_init( &attr );
	pthread_attr_setdetachstate(&attr, PTHREAD_CREATE_JOINABLE);

	for( unsigned int i = 0; i < NUM_THREADS; i++ ) {
		pthread_create( &threads[i], &attr, worker_thread, (void *) i );
	}

	for( unsigned int i = 0; i < NUM_THREADS; i++ ) {
		pthread_join( threads[i], NULL );
	}

	pthread_attr_destroy( &attr );
	pthread_cond_destroy( &cond_reader_done );
	pthread_cond_destroy( &cond_writer_done );
	pthread_mutex_destroy( &buffer_mutex );
}

