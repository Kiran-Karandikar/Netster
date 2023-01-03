/***************************************************************
 * Source File - Kiran Karandikar (kikarand)
 * CREATED: 09/01/2022
 *
 * First Networks Assignment: Creating an HTTP Client in C
 * A client in C that allows you to make GET and POST requests from the command
 * line.
 ***************************************************************
 */

#include <stdio.h>
#include <string.h>

void send_http(char* host, char* msg, char* resp, size_t len);

/*
  Implement a program that takes a host, verb, and path and
  prints the contents of the response from the request
  represented by that request.
 */
int main(int argc, char* argv[]) {
    if (argc != 4) {
        printf("Invalid arguments - %s <host> <GET|POST> <path>\n", argv[0]);
        return -1;
    }
    char* host = argv[1];
    char* verb = argv[2];
    char* path = argv[3];

    char msg[4096];
    char response[4096];

    snprintf(msg, sizeof msg, "%s %s HTTP/1.1\r\nHost:%s\r\n\r\n", verb, path,
             host);
    send_http(host, msg, response, sizeof response);
    printf("%s\n", response);

    return 0;
}
