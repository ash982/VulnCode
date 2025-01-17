#include "Class2.h"
#include <iostream>

Class2::Class2(const std::string& input) : input(input), db(nullptr) {}

Class2::~Class2() {
    if (db) {
        sqlite3_close(db);
    }
}

bool Class2::connectDb(const std::string& dbName) {
    int rc = sqlite3_open(dbName.c_str(), &db);
    if (rc) {
        std::cerr << "Can't open database: " << sqlite3_errmsg(db) << std::endl;
        return false;
    }
    return true;
}

void Class2::process() {
    std::cout << "Class2 processing: " << input << std::endl;
    if (!db) {
        std::cout << "Database not connected" << std::endl;
        return;
    }

    // Potentially unsafe operation
    std::string query = "SELECT * FROM users WHERE username = '" + input + "'";
    std::cout << "Executing query: " << query << std::endl;

    char* errMsg = nullptr;
    int rc = sqlite3_exec(db, query.c_str(), nullptr, nullptr, &errMsg);
    if (rc != SQLITE_OK) {
        std::cerr << "SQL error: " << errMsg << std::endl;
        sqlite3_free(errMsg);
    } else {
        std::cout << "Operation done successfully" << std::endl;
    }
}

