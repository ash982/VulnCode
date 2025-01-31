#include "file_handler.h"
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

void execute_script(FileHandler* handler) {
    char* const args[] = {handler->script_path, NULL};
    execv(handler->script_path, args);
}

void init_file_handler(FileHandler* handler, const char* script_path) {
    handler->script_path = strdup(script_path);
    handler->execute_script = execute_script;
}

void destroy_file_handler(FileHandler* handler) {
    free(handler->script_path);
}
