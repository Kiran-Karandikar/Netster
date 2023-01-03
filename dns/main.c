/***************************************************************
* Source File - Kiran Karandikar (kikarand)
* CREATED: 09/12/2022
*
* Use the `getaddrinfo` and `inet_ntop` functions to convert a string host and
integer port into a string dotted ip address and port.
*
* Note: This code references example given on man page for both `getaddrinfo`
* and `inet_ntop`.
***************************************************************
*/
#include <arpa/inet.h>
#include <netdb.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/types.h>

int main(int argc, char* argv[]) {
    if (argc != 3) {
        printf("Invalid arguments - %s <host> <port>", argv[0]);
        return -1;
    }
    char* host = argv[1];
    long port = atoi(argv[2]);
    int s;
    struct addrinfo hints, *result;
    int port_number_chars = 0;
    char* port_number;

    port_number_chars = snprintf(NULL, 0, "%ld", port) + 1;
    port_number = malloc(port_number_chars);
    snprintf(port_number, port_number_chars, "%ld", port);

    // man page for both `getaddrinfo`
    memset(&hints, 0, sizeof(hints));
    hints.ai_family = PF_UNSPEC;
    hints.ai_socktype = SOCK_STREAM;
    hints.ai_protocol = IPPROTO_TCP;
    hints.ai_flags = AI_PASSIVE;

    s = getaddrinfo(host, port_number, &hints, &result);
    // man page for both `getaddrinfo`
    if (s != 0) {
        fprintf(stderr, "getaddrinfo: %s\n", gai_strerror(s));
        exit(EXIT_FAILURE);
    }
    for (; result != NULL; result = result->ai_next) {
        void* raw_addr;
        char response[8192];
        // man page `inet_ntop`.
        if (result->ai_family == AF_INET) { // Address is IPv4
            struct sockaddr_in* tmp =
                (struct sockaddr_in*)
                    result->ai_addr; // Cast addr into AF_INET container
            raw_addr =
                &(tmp->sin_addr); // Extract the address from the container
            inet_ntop(AF_INET, raw_addr, response, sizeof response);
            printf("IPv4 %s\n", response);
        } else { // Address is IPv6
            struct sockaddr_in6* tmp =
                (struct sockaddr_in6*)
                    result->ai_addr; // Cast addr into AF_INET6 container
            raw_addr =
                &(tmp->sin6_addr); // Extract the address from the container
            inet_ntop(AF_INET6, raw_addr, response, sizeof response);
            printf("IPv6 %s\n", response);
        }
    }

    return 0;
}
