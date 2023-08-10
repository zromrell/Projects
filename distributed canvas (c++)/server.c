// server
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

// packet size
#define BUFSIZE 1024
#define BOARDDIMENSIONS 100
#define PORT 8080

void *run_thread(void *vargp);
double total_time_of_recieve_send;
pthread_mutex_t mutex;
struct clientInfo {
    char* IP_addr;
    int socket;
    bool connectionStatus;
};
int num_clients = 0;
struct node {
  struct clientInfo client;
  struct node *next;
  struct node *prev;
};
struct node *head = NULL;
struct node *last = NULL;
struct pixelUpdate {
  int index;
  int color;
};

int boardState[BOARDDIMENSIONS*BOARDDIMENSIONS];
bool isEmpty(){
  return head == NULL;
}

// Always adds clients to the end of list
void addClient(struct clientInfo obj){
  struct node *newClient = (struct node*) malloc(sizeof(struct node));
  newClient->client = obj;
  newClient->next = NULL;
  if (isEmpty()){
    head = newClient;
  } else {
    last->next = newClient;
    newClient->prev = last;
  }
  last = newClient;
  num_clients++;
}

// Removes a specific client
void removeClient(int connfd){
  struct node *initial = head;
  if(num_clients > 1){
    for(int i = 0; i < num_clients; i++){
      if(initial->client.socket == connfd){
        if (i == 0) {
          initial->next->prev = NULL;
          head = initial->next;
        } else if(i == num_clients-1){
          initial->prev->next = NULL;
          last = initial->prev;
        } else {
          initial->next->prev = initial->prev;
          initial->prev->next = initial->next;
        }
        free(initial);
        num_clients--;
        break;
      }
      initial = initial->next;
    }
  } else if (num_clients == 1) {
    head = NULL;
    last = NULL;
    free(initial);
    num_clients--;
  }
}


int main(int argc, char **argv) {
  printf("Server running...\n");
  printClients();
  for(int i = 0; i <BOARDDIMENSIONS*BOARDDIMENSIONS; i++){
    boardState[i] = 14;
  }
  
  int listenfd;        // listening socket
  int *connfd;         // connection socket 
  socklen_t clientlen; // byte size of client's address 
  pthread_t tid;       // thread id 

  // read struct
  struct sockaddr_in myaddr;  // my ip address info
  struct sockaddr_in clientaddr; // client's info

  // first, load up address structs
  myaddr.sin_port = htons(PORT);
  
  /* htons: Converts 16, 32, 64 bit quantities 
   * from network byte order (big endian) to/from 
   * host byte order (assuming little endian).
   */
  myaddr.sin_family = AF_INET;
  myaddr.sin_addr.s_addr = htonl(INADDR_ANY);
  // make a (server) socket
  listenfd = socket(AF_INET, SOCK_STREAM, 0); // domain = AF_INET, type = SOCK_STREAM, protocol = 0 or IPPROTO_TCP
  if (listenfd < 0) {
    printf("ERROR opening socket\n");
    exit(1);
  }

  /* setsockopt: Handy debugging trick that lets 
   * us rerun the server on same port immediately after we kill it; 
   * otherwise we have to wait about 20 secs. 
   * Eliminates "ERROR on binding: Address already in use" error.
   */
  int optval;
  optval = 1;
  if (setsockopt(listenfd, SOL_SOCKET, SO_REUSEADDR, (const void *)&optval , sizeof(int)) < 0){
    printf("ERROR on setsockopt\n");    
    exit(1);
  }

  // bind: associate the listening socket (listenfd) with a specific address/port
  if (bind(listenfd, (struct sockaddr*) &myaddr, sizeof(myaddr))<0) {
    printf("ERROR on binding\n");
    exit(1);
  }

  // listen on socket and allow for max pending connection queue of length 10
  if (listen(listenfd, 10) < 0) { 
    printf("ERROR on listen\n");
    exit(1);
  }

  // main loop: wait for a connection request, make thread
  while (1) {
    clientlen = sizeof(clientaddr);
    connfd = malloc(sizeof(int));
    *connfd = accept(listenfd, (struct sockaddr *)&clientaddr, &clientlen);
    if (connfd < 0) {
      printf("ERROR on accept\n");
      exit(1);
    }

    // store the information of the client
    char IPString[INET_ADDRSTRLEN];
    struct clientInfo client;
    inet_ntop(AF_INET, &(clientaddr.sin_addr), IPString, INET_ADDRSTRLEN);
    client.IP_addr = IPString;
    client.socket = *connfd;
    client.connectionStatus = true;
    pthread_mutex_lock(&mutex);
    addClient(client);
    pthread_mutex_unlock(&mutex);
    printClients();
    printf("Client %i connected!\n", client.socket);
    // try to create thread and run function "run_thread"
    if (pthread_create(&tid, NULL, run_thread, connfd) !=0) {
      printf("ERROR creating threads\n");
      exit(1);
    }
  }
  return 0; 
}

void printClients(){
  struct node *initial = head;
  if (isEmpty()) {
        printf("empty mofo\n");
  } else {
    for(int i=0; i < num_clients; i++){
      if (initial->client.socket == last->client.socket) {
        printf("%i\n",initial->client.socket);
      } else {
        printf("%i -> ",initial->client.socket);
      }
      initial = initial->next;
    }
  }
}



void broadCast(int pixidx, int connfd) {
  struct pixelUpdate message = {pixidx, boardState[pixidx]};
  int message_length = sizeof(message);
  struct node *initial = head;
  for(int i=0; i < num_clients; i++){
    if(initial->client.socket != connfd){
      int connfd1 = initial->client.socket;
      int x; x = 0;
      // send while OS is slacking
      while (x < message_length) {
        x += send(connfd1, &message+x, message_length-x, 0);
      } 
    }
    initial = initial->next;
  }
}


void *run_thread(void *vargp) {
  int connfd = *((int *)vargp);  // client socket fd 
  struct pixelUpdate message; //bzero(message, sizeof(struct pixelUpdate)); // message buffer for edits
  int num_read;  // tally of bytes read  
  // detach this thread from parent thread
  if (pthread_detach(pthread_self()) != 0){
    printf("ERROR detaching\n");
    exit(1);
  }
  free(vargp); // free heap space for vargp since we have connfd
  
  // send the contents of the board
  //printf("Sending Contents to \n");  
  int board_size = sizeof(boardState);
  int x;
  x = 0;
  while (x < board_size){
    x += send(connfd, boardState+x, board_size-x, 0);
  }

  // keep a persistent connection
  while(1){
    // print time between each recieve and send on server side
    clock_t start, end;
    start = clock();
    if((num_read = recv(connfd, &message, sizeof(struct pixelUpdate), 0)) < 0){
      printf("ERROR reading from socket\n");
      continue;
    } else if (num_read == 0){
      removeClient(connfd);
      printClients();
      printf("Client %i disconnected!!\n",connfd);
      break;
    } else{
      pthread_mutex_lock(&mutex);
      boardState[message.index] = message.color;
      pthread_mutex_unlock(&mutex);
      //broadcast change
      broadCast(message.index, connfd);
    }
    end = clock();
    pthread_mutex_lock(&mutex);
    //printf("time added %f\n", ((double) (end - start)) / CLOCKS_PER_SEC);
    total_time_of_recieve_send += ((double) (end - start)) / CLOCKS_PER_SEC;
    //printf("time %f\n", total_time_of_board);
    pthread_mutex_unlock(&mutex);
    
  } 
  printf("total_time %f\n", total_time_of_recieve_send);
  shutdown(connfd, 0);
  close(connfd);
  return NULL;
}
