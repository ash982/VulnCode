#ifndef CLASS1_H
#define CLASS1_H

typedef struct Class1 Class1;

Class1* class1_create(const char* input);
void class1_process(Class1* self);
void class1_destroy(Class1* self);

#endif
