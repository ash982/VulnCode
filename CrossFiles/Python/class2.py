import sqlite3

class Class2:
    def __init__(self, input_data):
        self.input = input_data
        self.db = None

    def connect_db(self, db_name):
        try:
            self.db = sqlite3.connect(db_name)
            return True
        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")
            return False

    def process(self):
        print(f"Class2 processing: {self.input}")
        if not self.db:
            print("Database not connected")
            return

        # Potentially unsafe operation
        query = f"SELECT * FROM users WHERE username = '{self.input}'"
        print(f"Executing query: {query}")

        try:
            cursor = self.db.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            print(f"Query results: {results}")
        except sqlite3.Error as e:
            print(f"Error executing query: {e}")

    def __del__(self):
        if self.db:
            self.db.close()

