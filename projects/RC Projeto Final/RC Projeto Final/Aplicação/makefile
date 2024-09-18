CC = gcc
CFLAGS = -Wall -Wextra -pthread

all: server client

server: server/sv_main.o server/sv_shm.o server/sv_tcp.o server/sv_udp.o
	$(CC) $(CFLAGS) -o server/server server/sv_main.o server/sv_shm.o server/sv_tcp.o server/sv_udp.o

client: client/client.o
	$(CC) $(CFLAGS) -o client/client client/client.o

server/sv_main.o: server/sv_main.c server/sv_main.h
	$(CC) $(CFLAGS) -c server/sv_main.c -o server/sv_main.o

server/sv_shm.o: server/sv_shm.c server/sv_shm.h
	$(CC) $(CFLAGS) -c server/sv_shm.c -o server/sv_shm.o

server/sv_tcp.o: server/sv_tcp.c server/sv_tcp.h
	$(CC) $(CFLAGS) -c server/sv_tcp.c -o server/sv_tcp.o

server/sv_udp.o: server/sv_udp.c server/sv_udp.h
	$(CC) $(CFLAGS) -c server/sv_udp.c -o server/sv_udp.o

client/client.o: client/client.c
	$(CC) $(CFLAGS) -c client/client.c -o client/client.o

clean:
	rm -f server/*.o server/server client/*.o client/client
