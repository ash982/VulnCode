#ifndef CLASS2_H
#define CLASS2_H

typedef struct Class2 Class2;

Class2* class2_create(const char* input);
int class2_connect_db(Class2* self, const char* db_name);
void class2_process(Class2* self);
void class2_destroy(Class2* self);
