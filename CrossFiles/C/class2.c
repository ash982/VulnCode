#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sqlite3.h>
#include "class2.h"

struct Class2 {
    char* input;
    sqlite3* db;
};

Class2* class2_create(const char* input) {
    Class2* self = malloc(sizeof(Class2));
    self->input = strdup(input);
    self->db = NULL;
    return self;
}

int class2_connect_db(Class2* self, const char* db_name) {
    int rc = sqlite3_open(db_name, &(self->db));
    if (rc) {
        fprintf(stderr, "Can't open database: %s\n", sqlite3_errmsg(self->db));
        return 0;
    }
    return 1;
}

void class2_process(Class2* self) {
    printf("Class2 processing: %s\n", self->input);

    if (!self->db) {
        fprintf(stderr, "Database not connected\n");
        return;
    }

    char query[256];
    snprintf(query, sizeof(query), "SELECT * FROM users WHERE username = '%s'", self->input);
    printf("Executing query: %s\n", query);

    char* err_msg = 0;
    int rc = sqlite3_exec(self->db, query, 0, 0, &err_msg);
    
    if (rc != SQLITE_OK) {
        fprintf(stderr, "SQL error: %s\n", err_msg);
        sqlite3_free(err_msg);
    } else {
        printf("Operation done successfully\n");
    }
}

void class2_destroy(Class2* self) {
    if (self->db) {
        sqlite3_close(self->db);
    }
    free(self->input);
    free(self);
}
