#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/select.h>

#define SERVER_PORT 1234
#define BUFFER_SIZE 1024
#define MAX_CLIENTS 5

int main() {
    int listen_fd, connect_fd[MAX_CLIENTS];
    struct sockaddr_in server_addr, client_addr;
    socklen_t client_addr_len;
    char buffer[BUFFER_SIZE];
    int max_fd, activity, i, valread;
    fd_set readfds;

    listen_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (listen_fd == -1) {
        perror("socket");
        exit(1);
    }

    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = htonl(INADDR_ANY);
    server_addr.sin_port = htons(SERVER_PORT);

    if (bind(listen_fd, (struct sockaddr*)&server_addr, sizeof(server_addr)) == -1) {
        perror("bind");
        exit(1);
    }

    if (listen(listen_fd, MAX_CLIENTS) == -1) {
        perror("listen");
        exit(1);
    }

    printf("Server Listening on Port %d\n", SERVER_PORT);

    for (i = 0; i < MAX_CLIENTS; i++) {
        connect_fd[i] = 0;
    }

    while (1) {
        FD_ZERO(&readfds);
        FD_SET(listen_fd, &readfds);
        max_fd = listen_fd;

        for (i = 0; i < MAX_CLIENTS; i++) {
            int fd = connect_fd[i];
            if (fd > 0) {
                FD_SET(fd, &readfds);
            }
            if (fd > max_fd) {
                max_fd = fd;
            }
        }

        activity = select(max_fd + 1, &readfds, NULL, NULL, NULL);
        if (activity < 0) {
            perror("select");
        }

        if (FD_ISSET(listen_fd, &readfds)) {
            client_addr_len = sizeof(client_addr);
            int new_socket = accept(listen_fd, (struct sockaddr*)&client_addr, &client_addr_len);
            if (new_socket < 0) {
                perror("accept");
            }
            printf("New connection, socket fd is %d, IP is : %s, port : %d\n",
                   new_socket, inet_ntoa(client_addr.sin_addr), ntohs(client_addr.sin_port));
            for (i = 0; i < MAX_CLIENTS; i++) {
                if (connect_fd[i] == 0) {
                    connect_fd[i] = new_socket;
                    break;
                }
            }
        }

        for (i = 0; i < MAX_CLIENTS; i++) {
            int fd = connect_fd[i];
            if (FD_ISSET(fd, &readfds)) {
                valread = read(fd, buffer, BUFFER_SIZE);
                if (valread == 0) {
                    getpeername(fd, (struct sockaddr*)&client_addr, &client_addr_len);
                    printf("Host disconnected, IP %s, port %d\n",
                           inet_ntoa(client_addr.sin_addr), ntohs(client_addr.sin_port));
                    close(fd);
                    connect_fd[i] = 0;
                } else {
                    buffer[valread] = '\0';
                    for (int j = 0; j < MAX_CLIENTS; j++) {
                        if (connect_fd[j] != 0 && connect_fd[j] != fd) {
                            send(connect_fd[j], buffer, strlen(buffer), 0);
                        }
                    }
                }
            }
        }
    }

    for (i = 0; i < MAX_CLIENTS; i++) {
        if (connect_fd[i] != 0) {
            close(connect_fd[i]);
        }
    }
    close(listen_fd);

    return 0;
}