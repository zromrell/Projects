// webserver.c 
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

void *run_thread(void *vargp);
void error_header(int connfd, int error_type, char* connection_type);
void send101(int message_length, int connfd, char* message); 
void send_header(int connfd, int fd, char* filename, char* connection_type);
int open_thread_count = 0;
pthread_mutex_t mutex;
char root[BUFSIZE]; 

int main(int argc, char **argv) {
  int listenfd;        // listening socket
  int *connfd;         // connection socket 
  int portno;          // port to listen on 
  socklen_t clientlen; // byte size of client's address 
  pthread_t tid;       // thread id 

  // read struct
  struct sockaddr_in myaddr;  // my ip address info
  struct sockaddr clientaddr; // client's info

  // check command line args
  if (argc != 5 || (strcmp(argv[1], "-document_root") != 0) || (strcmp(argv[3], "-port") != 0)) {
    fprintf(stderr, "usage: %s -document_root <path> -port <port>\n", argv[0]);
    exit(1);
  }

  // set root
  bzero(root, BUFSIZE);
  strcpy(root, argv[2]);
  // "x" -> int x
  portno = atoi(argv[4]);
  
  
  // first, load up address structs
  myaddr.sin_port = htons(portno);
  
  
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
  if (bind(listenfd, (struct sockaddr*) &myaddr, sizeof(myaddr)) <0) {
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
    // accept: wait for a connection request
    clientlen = sizeof(clientaddr);
    // allocation of clients file descriptor on heap... thread-safe
    connfd = malloc(sizeof(int));
    *connfd = accept(listenfd, (struct sockaddr *)&clientaddr, &clientlen);

    if (connfd < 0) {
      printf("ERROR on accept\n");
      exit(1);
    }

    printf("Client connected!\n");
    // try to create thread and run function "run_thread"
    if (pthread_create(&tid, NULL, run_thread, connfd) !=0) {
      printf("error creating threads\n");
      exit(1);
    }
  }
  return 0; 
}






void error_header(int connfd, int errorType, char* connection_type){
  char message[BUFSIZE]; bzero(message, BUFSIZE);
  //date                                                                     
  time_t t = time(NULL);
  struct tm tm = *localtime(&t);
  char date[BUFSIZE]; bzero(date, BUFSIZE);
  sprintf(date,"Date: %d-%02d-%02d %02d:%02d:%02d\n", tm.tm_year + 1900, tm.tm_mon+1, tm.tm_hour, tm.tm_mday,tm.tm_min, tm.tm_sec);

  // content-length string
  char text[BUFSIZE]; bzero(text, BUFSIZE);
  
  // send error
  if (errorType == 400){
    //400 headers
    strcpy(message, connection_type);
    strcpy(message + 8, " 400 Bad Request\n");
    strcat(message, date);
    sprintf(text, "Content-Length: %lu\n", strlen("400 Bad Request\n"));
    strcat(message, text);
    strcat(message, "Content-Type: text/plain\r\n\r\n");
    send101(strlen(message), connfd, message);
    //message body
    send101(strlen("400 Bad Request\n"), connfd, "400 Bad Request\n");
  } else if (errorType == 403) {
    //403 headers
    strcpy(message, connection_type);
    strcpy(message + 8, " 403 Forbidden\n");
    strcat(message, date);
    sprintf(text, "Content-Length: %lu\n", strlen("403 Forbidden\n"));
    strcat(message, text);
    strcat(message, "Content-Type: text/plain\r\n\r\n");
    send101(strlen(message), connfd, message);
    //message body
    send101(strlen("403 Forbidden... nice try :(\n"), connfd, "403 Forbidden... nice try :(\n");
  } else if (errorType == 404) {
    //404 headers
    strcpy(message, connection_type);
    strcpy(message + 8, " 404 Not Found\n");
    strcat(message, date);
    sprintf(text, "Content-Length: %lu\n", strlen("404 Not Found\n"));
    strcat(message, text);
    strcat(message, "Content-Type: text/plain\r\n\r\n");
    send101(strlen(message), connfd, message);
    //message body
    send101(strlen("404 Not Found\n"), connfd, "404 Not Found\n");
  } else if (errorType == 501) {
    //501 headers
    strcpy(message, connection_type);
    strcpy(message + 8, " 501 Not Implemented\n");
    strcat(message, date);
    sprintf(text, "Content-Length: %lu\n", strlen("501 Not Implemented\n"));
    strcat(message, text);
    strcat(message, "Content-Type: text/plain\r\n\r\n");
    send101(strlen(message), connfd, message);
    //message body
    send101(strlen("501 Not Implemented\n"), connfd, "501 Not Implemented\n");
  } else if (errorType == 502) {
    //502 headers
    strcpy(message, connection_type);
    strcpy(message + 8, " 502 Bad Gateway\n");
    strcat(message, date);
    sprintf(text, "Content-Length: %lu\n", strlen("502 Bad Gateway\n"));
    strcat(message, text);
    strcat(message, "Content-Type: text/plain\r\n\r\n");
    send101(strlen(message), connfd, message);
    //message body
    send101(strlen("502 Bad Gateway\n"), connfd, "502 Bad Gateway\n");
  }
}






void send_header(int connfd, int fd, char* filepath, char*  connection_type){
  //200 OK
  char* message = (char *) malloc(BUFSIZE); bzero(message, BUFSIZE);
  strcpy(message, connection_type);
  strcpy(message + 8, " 200 OK\n");
  
  //date
  time_t t = time(NULL);
  struct tm tm = *localtime(&t);
  char date[BUFSIZE]; bzero(date, BUFSIZE);
  sprintf(date,"Date: %d-%02d-%02d %02d:%02d:%02d\n", tm.tm_year + 1900, tm.tm_mon+1, tm.tm_hour, tm.tm_mday,tm.tm_min, tm.tm_sec);
  strcat(message, date);

  //content-length
  //read size, rewind tape
  int length;
  length = lseek(fd, 0L, SEEK_END);
  lseek(fd, 0L, SEEK_SET);
  //conversion to string
  char text[BUFSIZE]; bzero(text, BUFSIZE);
  sprintf(text, "Content-Length: %d\n", length);
  strcat(message, text);

  //content-type
  if(strncmp(filepath + strnlen(filepath, BUFSIZE) - 5, ".html", 5) == 0){
    // add content type (html)
    strcat(message, "Content-Type: text/html\r\n\r\n");
  } else if (strncmp(filepath + strnlen(filepath, BUFSIZE) - 4, ".gif", 4) == 0){ 
    // add content type (gif)
    strcat(message, "Content-Type: image/gif\r\n\r\n");
  } else if (strncmp(filepath + strnlen(filepath, BUFSIZE) - 4, ".jpg", 4) == 0){
    // add content type (jpg)
    strcat(message, "Content-Type: image/jpg\r\n\r\n");
  } else if (strncmp(filepath + strnlen(filepath, BUFSIZE) - 4, ".ico", 4) == 0){
    // add content type (ico)
    strcat(message, "Content-Type: image/vnd\r\n\r\n");
  } else if (strncmp(filepath + strnlen(filepath, BUFSIZE) - 4, ".txt", 4) == 0){
    // add content type (txt)
    strcat(message, "Content-Type: text/plain\r\n\r\n");
  }
  send101(strlen(message), connfd, message);
  if (message) free(message);
}






void send101(int message_length,int connfd, char* message){
  // count packets sent
  int x; x = 0;
  // send while OS is slacking
  while (x < message_length) {
    x += send(connfd, message+x, message_length-x, 0);
  }
}






void *run_thread(void *vargp) {
  //increment count
  pthread_mutex_lock(&mutex);
  open_thread_count += 1;
  pthread_mutex_unlock(&mutex);
  
  //init
  char message[BUFSIZE];         // message buffer
  char connection_type[BUFSIZE]; // 1.0 vs 1.1
  int num_read;                  // tally of bytes read  
  int connfd = *((int *)vargp);  // client fd 

  // requested file
  char filename[BUFSIZE];
  char filepath[BUFSIZE];
  
  // detach this thread from parent thread
  if (pthread_detach(pthread_self()) != 0){
    printf("error detaching\n");
    exit(1);
  }

  free(vargp); // free heap space for vargp since we have connfd
  
  // assume HTTP/1.1 and break at end if HTTP/1.0
  while(1){
    bzero(message, BUFSIZE); // slow OS, memory error
    bzero(connection_type, BUFSIZE); // slow OS, memory error
    bzero(filename, BUFSIZE); // slow OS, memory error
    bzero(filepath, BUFSIZE); // slow OS, memory error

    // thread's timeout val
    struct timeval timeout;
    timeout.tv_sec = 5 + 50/open_thread_count;
    timeout.tv_usec = 0;
    if (setsockopt(connfd, SOL_SOCKET, SO_RCVTIMEO, (const void *)&timeout , sizeof(timeout)) < 0){
      printf("ERROR on setsockopt\n");
      return NULL;
    }
    
    if((num_read = recv(connfd, message, BUFSIZE, 0)) < 0){
      if (errno == EAGAIN || errno == ETIMEDOUT){
	break;
      }
      printf("ERROR reading from socket\n");
      continue;
    } else if (num_read == 0){
      break;
    }

    // first line 
    char request[BUFSIZE]; bzero(request, BUFSIZE);
    for(int i = 0; message[i] != '\n' && i < BUFSIZE; ++i){   
      request[i] = message[i];
    }
   
    // connection type
    strncat(connection_type, request + strlen(request) - 9, 9);
    // get root
    strcpy(filepath, root);	     

    // GET command
    if (strncmp("GET /", request, 5) == 0) {
      // updating file path
      for(int i = 4; request[i] != ' ' && i < BUFSIZE - 4; ++i){
	filepath[strlen(filepath)] = request[i];
      }
      // GET / shortcut
      if (strlen(filepath) == strlen(root)+1){
	strcat(filepath, "index.html");
      }
      // don't allow moving folders
      if (strncmp((filepath+strlen(root)), "/../", 4) == 0){
	error_header(connfd, 403, connection_type);
        printf("File Forbbiden\n");
        continue;
      }
      
      struct stat fileStat;
      // 404 Not Found
      int y;
      if((y = stat(filepath, &fileStat)) < 0) {
	printf("%d\n", y);
	error_header(connfd, 404, connection_type);
	printf("File Not Found\n");
	continue;
      }
      // 403 Forbidden
      if (!(fileStat.st_mode & S_IROTH)) {
	error_header(connfd, 403, connection_type);
	printf("File Forbbiden\n");
	continue;
      }
      
      // open file
      int filedescriptor;
      if ((filedescriptor = open(filepath, O_RDONLY)) < 0) {
	// 502 Bad Gateway
	error_header(connfd, 502, connection_type);
	printf("ERROR reading file\n");
	continue;
      }
      
      //WOULD BE MORE EFFICIENT TO PARSE FILE TYPE HERE
      send_header(connfd, filedescriptor, filepath, connection_type);
      
      // send data
      char packet[BUFSIZE]; bzero(packet, BUFSIZE);
      int packet_size;
      
      // send packets by BUFSIZE constant
      int x;
      while((packet_size = read(filedescriptor, packet, BUFSIZE)) > 0){
	x = 0;
	while (x < packet_size){
	  x += send(connfd, packet+x, packet_size-x, 0);
	}
       	if (x < 0)  {
	  // 502 Bad Gateway
	  error_header(connfd, 502, connection_type);
	  printf("ERROR writing to socket\n");
	  continue;
	}
      }
      close(filedescriptor);      
      
    } else if (strncmp("HEAD /", request, 6) == 0) {
      // implement if have time
    } else if (strncmp("PUT /",request, 5) == 0|| strncmp("PUSH /", request, 6) == 0 || strncmp("TRACE /", request, 7) == 0){
      // 501 Not Implemented
      error_header(connfd, 501, connection_type);
    } else {
      // 400 Invalid Request (syntax or message framing)
      error_header(connfd, 400, connection_type);
    }
    // HTTP/1.0
    if (strncmp(connection_type, "HTTP/1.0", 8) == 0){
      break;
    }
  } 
 
  pthread_mutex_lock(&mutex);
  open_thread_count -= 1;
  pthread_mutex_unlock(&mutex);
  shutdown(connfd, 0);
  close(connfd);
  return NULL;
}
