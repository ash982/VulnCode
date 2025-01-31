#ifndef FILE_HANDLER_H
#define FILE_HANDLER_H

typedef struct FileHandler {
    char* script_path;
    void (*execute_script)(struct FileHandler*);
} FileHandler;

void init_file_handler(FileHandler* handler, const char* script_path);
void destroy_file_handler(FileHandler* handler);

#endif
