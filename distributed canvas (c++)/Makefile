CC=gcc
CFLAGS=-g -O2 -Wall
LDLIBS=-lpthread

all: server abclient client

server: server.c 

abclient: abclient.c

client: client.c

clean:
	rm -rf *.o *~ *.dSYM server abclient client
