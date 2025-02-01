#include "file_handler.h"
#include <stdio.h>
#include <sys/wait.h>
#include <unistd.h>

int main() {
    FileHandler handler;
    init_file_handler(&handler, "./../bash/remove_xml_2020.sh");

    pid_t pid = fork();

    if (pid == 0) {
        // Child process
        handler.execute_script(&handler);
        // If we reach here, exec failed
        perror("exec failed");
        exit(1);
    } else if (pid > 0) {
        // Parent process
        int status;
        waitpid(pid, &status, 0);
        printf("Script execution completed with status %d\n", status);
    } else {
        // Fork failed
        perror("fork failed");
        return 1;
    }

    destroy_file_handler(&handler);
    return 0;
}
