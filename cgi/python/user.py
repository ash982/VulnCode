#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib'))

import cgi
import cgitb
import json
from database import get_db_connection

cgitb.enable()

def main():
    print("Content-Type: application/json\n")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, email FROM users")
        users = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        print(json.dumps({
            "status": "success",
            "data": users
        }))
        
    except Exception as e:
        print(json.dumps({
            "status": "error",
            "message": str(e)
        }))

if __name__ == "__main__":
    main()
