#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
#include <netdb.h>
#include <sys/types.h> 
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <pthread.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <time.h>
#include <errno.h>

#define CANVAS_WIDTH 100
#define CANVAS_HEIGHT 100
#define NUM_COLORS 15
#define PORT 8080
int client_fd;
struct pixelUpdate {
  int index;
  int color;
};

void broadCast(struct pixelUpdate pixel) {
    int message_length = sizeof(pixel);
    int x; x = 0;
    // send while OS is slacking
    while (x < message_length) {
        x += send(client_fd, &pixel+x, message_length-x, 0);
    }
}

int main() {
    int status;
    struct sockaddr_in serv_addr;
    if ((client_fd = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
        printf("Socket creation error\n");
        return -1;
    }
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(PORT);
    //char* IPAddress = "137.165.172.177"; // IP addr of local host
    char* IPAddress = "137.165.8.10";

    // Convert IPv4 and IPv6 addresses from text to binary form
    if (inet_pton(AF_INET, IPAddress, &serv_addr.sin_addr) <= 0) {
        printf("Invalid address/Address not supported \n");
        return -1;
    }
    if ((status = connect(client_fd, (struct sockaddr*) &serv_addr, sizeof(serv_addr))) < 0) {
        printf("Connection Failed \n");
        return -1;
    }
    int num_read;
    int initialBoard[CANVAS_HEIGHT*CANVAS_WIDTH];
    if((num_read = recv(client_fd, initialBoard, sizeof(initialBoard), 0)) < 0){
            printf("ERROR reading from socket\n");
            exit(0);
    }

    int randIndex;
    int randColor;
    struct pixelUpdate randUpdate;
    for (int i = 0; i < 10000; i++){
        randIndex = rand() % (CANVAS_HEIGHT*CANVAS_WIDTH);
        randColor = rand() % 15;
        randUpdate.index = randIndex;
        randUpdate.color = randColor;
        broadCast(randUpdate);
    }
    while(1){

    }
    // closing the connected socket
    close(client_fd);
    return 0;
}
