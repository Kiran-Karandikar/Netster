/***************************************************************
 * Source File - Kiran Karandikar (kikarand)
 * CREATED: 09/06/2022
 *
 * Use the provided 'connect_smtp' and 'send_smtp' functions
 * to connect to the "lunar.open.sice.indian.edu" smtp relay
 * and send the commands to write emails as described in the
 * assignment wiki.
 ***************************************************************
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int connect_smtp(const char* host, int port);
void send_smtp(int sock, const char* msg, char* resp, size_t len);

int main(int argc, char* argv[]) {
    if (argc != 3) {
        printf("Invalid arguments - %s <email-to> <email-filepath>", argv[0]);
        return -1;
    }

    char* rcpt = argv[1];
    char* filepath = argv[2];
    char from[300];
    char rcpt_to[300];
    char file_contents[4096];
    char message[5120];
    char response[4096];
    FILE* ptr;
    size_t sz = 1;
    int socket = connect_smtp("lunar.open.sice.indiana.edu", 25);

    strcpy(from, "MAIL FROM:");
    strcat(from, rcpt);
    strcat(from, "\n");

    strcpy(rcpt_to, "RCPT TO:");
    strcat(rcpt_to, rcpt);
    strcat(rcpt_to, "\n");

    printf("%s\n", rcpt);

    ptr = fopen(filepath, "r");
    if (NULL == ptr) {
        printf("file can't be opened \n");
    } else {
        while (sz > 0) {
            sz = fread(file_contents, 1, 4096, ptr);
        }

        fclose(ptr);
    }
    strcpy(message, file_contents);
    strcat(message, "\r\n.\r\n");
    send_smtp(socket, "HELO iu.edu\n", response, sizeof response);
    printf("%s\n", response);
    send_smtp(socket, from, response, sizeof response);
    printf("%s\n", response);
    send_smtp(socket, rcpt_to, response, sizeof response);
    printf("%s\n", response);
    send_smtp(socket, "DATA\n", response, sizeof response);
    printf("%s\n", response);
    send_smtp(socket, message, response, sizeof response);
    printf("%s\n", response);
    send_smtp(socket, "QUIT\n", response, sizeof response);
    return 0;
}
