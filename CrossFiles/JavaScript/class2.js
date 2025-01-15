const sqlite3 = require('sqlite3').verbose();

class Class2 {
    constructor(input) {
        this.input = input;
        this.db = null;
    }

    connectDb(dbName) {
        return new Promise((resolve, reject) => {
            this.db = new sqlite3.Database(dbName, (err) => {
                if (err) {
                    console.error('Could not connect to database', err);
                    reject(err);
                } else {
                    resolve();
                }
            });
        });
    }

    process() {
        console.log(`Class2 processing: ${this.input}`);
        if (!this.db) {
            console.log("Database not connected");
            return;
        }

        // Potentially unsafe operation
        const query = `SELECT * FROM users WHERE username = '${this.input}'`;
        console.log(`Executing query: ${query}`);

        this.db.all(query, [], (err, rows) => {
            if (err) {
                console.error("Error executing query:", err);
            } else {
                console.log("Query results:", rows);
            }
        });
    }

    closeDb() {
        if (this.db) {
            this.db.close();
        }
    }
}

module.exports = Class2;
