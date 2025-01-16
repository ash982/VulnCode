import sqlite3 from 'sqlite3';

export class Class2 {
    private input: string;
    private db: sqlite3.Database | null;

    constructor(input: string) {
        this.input = input;
        this.db = null;
    }

    public connectDb(dbName: string): Promise<void> {
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

    public process(): void {
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

    public closeDb(): void {
        if (this.db) {
            this.db.close();
        }
    }
}
