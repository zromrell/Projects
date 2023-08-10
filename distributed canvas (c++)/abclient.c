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
#define NUM_THREADS 100
void *run_thread(void *vargp);
pthread_mutex_t mutex;
double total_time_of_board;
pthread_t threadIDs[NUM_THREADS] = {0};
struct pixelUpdate {
  int index;
  int color;
};

void broadCast(struct pixelUpdate pixel, int connfd) {
    int message_length = sizeof(pixel);
    int x; x = 0;
    // send while OS is slacking
    while (x < message_length) {
        x += send(connfd, &pixel+x, message_length-x, 0);
    }
}

int main() {
    struct sockaddr_in serv_addr;
    pthread_t tid;       // thread id 
    //char* IPAddress = "137.165.172.177"; // IP addr of local host
    int connfd;
    int status;
    // main loop: create clients
    for (int i = 0; i < NUM_THREADS; i++){
        if ((connfd = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
            printf("Socket creation error\n");
            return -1;
        }
        //printf("connfd %d\n", connfd);
        serv_addr.sin_family = AF_INET;
        serv_addr.sin_port = htons(PORT);
	
        char* IPAddress = "137.165.8.10";
	
        // Convert IPv4 and IPv6 addresses from text to binary form
        if (inet_pton(AF_INET, IPAddress, &serv_addr.sin_addr) <= 0) {
            printf("Invalid address/Address not supported \n");
            return -1;
        }
        if ((status = connect(connfd, (struct sockaddr*) &serv_addr, sizeof(serv_addr))) < 0) {
            printf("Connection Failed \n");
            return -1;
        }
        //printf("Client %d connected and thread activated...\n", i);
        // try to create thread and run function "run_thread"
        void *vargs = (void *) malloc(sizeof(int));
        ((int *) vargs)[0] = connfd;
        if (pthread_create(&tid, NULL, run_thread, vargs) !=0) {
            printf("ERROR creating threads\n");
            exit(1);
        }
        threadIDs[i] = tid;
    }

    for (int i = 0; i < NUM_THREADS; i++){
        pthread_join(threadIDs[i], NULL);
    }
    //sleep(10);
    printf("Num_threads %i avg time %f\n", NUM_THREADS, total_time_of_board/NUM_THREADS);
    pthread_exit(NULL);
    return 0;
}

void *run_thread(void *vargp) {
    //printf("block0\n");
    //printf("vargp %d\n", ((int *)vargp)[0]);
    int connfd1 = ((int *)vargp)[0];  // server socket fd 
    // detach this thread from parent thread
    if (pthread_detach(pthread_self()) != 0){
        printf("ERROR detaching\n");
        exit(1);
    }
    free(vargp); // free heap space for vargp since we have connfd

    //recieve the contents of the board
    int num_read;
    int initialBoard[CANVAS_HEIGHT*CANVAS_WIDTH];
    // get time to recieve board...
    clock_t start, end;
    start = clock();
    if((num_read = recv(connfd1, initialBoard, sizeof(initialBoard), 0)) < 0){
        perror("ERROR reading from socket");
        return 0;
    }
    end = clock();
    
    pthread_mutex_lock(&mutex);
    //printf("time added %f\n", ((double) (end - start)) / CLOCKS_PER_SEC);
    total_time_of_board += ((double) (end - start)) / CLOCKS_PER_SEC;
    //printf("time %f\n", total_time_of_board);
    pthread_mutex_unlock(&mutex);
    
    // int randIndex;
    // int randColor;
    // struct pixelUpdate randUpdate;
    // for (int i = 0; i < 100; i++){
    //     randIndex = rand() % (CANVAS_HEIGHT*CANVAS_WIDTH);
    //     randColor = rand() % 15;
    //     randUpdate.index = randIndex;
    //     randUpdate.color = randColor;
    //     broadCast(randUpdate, connfd1);
    // }
    // printf("sent, pixels\n");
    
    shutdown(connfd1, 0);
    close(connfd1);
    return NULL;
}
