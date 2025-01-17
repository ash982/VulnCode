#ifndef CLASS2_H
#define CLASS2_H

#include <string>
#include <sqlite3.h>

class Class2 {
private:
    std::string input;
    sqlite3* db;

public:
    Class2(const std::string& input);
    ~Class2();
    bool connectDb(const std::string& dbName);
    void process();
};

#endif
