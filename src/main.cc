#include "controller.h"
#include "log_message.h"
#include <iostream>
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>

#define DEFAULT_PID_FILE        "/run/oresat-gpsd.pid"


int main (int argc, char *argv[]) {
    int c;
    std::string pid_file(DEFAULT_PID_FILE);
    FILE *run_fp = NULL;
    pid_t pid = 0, sid = 0;
    bool daemon_flag = false;

    // Register signal handlers
    signal(SIGINT, NULL);
    signal(SIGTERM, NULL);

    // Command line argument processing
    while ((c = getopt(argc, argv, "d")) != -1) {
        switch (c) {
            case 'd':
                daemon_flag = true;
                break;
            case '?':
                fprintf(stderr, "Uknown flag\n");
                exit(EXIT_FAILURE);
            default:
                fprintf(stderr, "Usage: %s [-d] [-l link]\n", argv[0]);
                exit(EXIT_FAILURE);
        }
    }

    setlogmask(LOG_UPTO(LOG_NOTICE));
    openlog(argv[0], LOG_PID|LOG_CONS, LOG_DAEMON);

    /* Run as daemon if needed */
    if (daemon_flag) {
        log_message(LOG_DEBUG, "Starting as daemon...\n");
        /* Fork */
        if ((pid = fork()) < 0) {
            log_message(LOG_ERR, "Error: Failed to fork!\n");
            exit(EXIT_FAILURE);
        }

        /* Parent process exits */
        if (pid) {
            exit(EXIT_SUCCESS);
        }

        /* Child process continues on */
        /* Log PID */
        if ((run_fp = fopen(pid_file.c_str(), "w+")) == NULL) {
            log_message(LOG_ERR, "Error: Unable to open file %s\n", pid_file.c_str());
            exit(EXIT_FAILURE);
        }
        fprintf(run_fp, "%d\n", getpid());
        fflush(run_fp);
        fclose(run_fp);

        /* Create new session for process group leader */
        if ((sid = setsid()) < 0) {
            log_message(LOG_ERR, "Error: Failed to create new session!\n");
            exit(EXIT_FAILURE);
        }

        /* Set default umask and cd to root to avoid blocking filesystems */
        umask(0);
        if (chdir("/") < 0) {
            log_message(LOG_ERR, "Error: Failed to chdir to root: %s\n", strerror(errno));
            exit(EXIT_FAILURE);
        }

        /* Redirect std streams to /dev/null */
        if (freopen("/dev/null", "r", stdin) == NULL) {
            log_message(LOG_ERR, "Error: Failed to redirect streams to /dev/null!\n");
            exit(EXIT_FAILURE);
        }
        if (freopen("/dev/null", "w+", stdout) == NULL) {
            log_message(LOG_ERR, "Error: Failed to redirect streams to /dev/null!\n");
            exit(EXIT_FAILURE);
        }
    }

    gps_wrapper_main();

    return 1;
}

