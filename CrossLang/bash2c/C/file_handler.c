#include "file_handler.h"
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

void execute_script(FileHandler* handler) {
    char cmdbuf[256];
    snprintf(cmdbuf, sizeof(cmdbuf), "sh -c %s", handler->script_path);
    execl("/bin/sh", "sh", "-c", cmdbuf, NULL);
}

void init_file_handler(FileHandler* handler, const char* script_path) {
    handler->script_path = strdup(script_path);
    handler->execute_script = execute_script;
}

void destroy_file_handler(FileHandler* handler) {
    free(handler->script_path);
}
