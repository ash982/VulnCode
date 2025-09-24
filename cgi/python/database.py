#!/usr/bin/env python3

import sqlite3
import datetime
from config import DATABASE_PATH

def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def save_contact_message(name, email, message):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO contact_messages (name, email, message, created_at)
        VALUES (?, ?, ?, ?)
    ''', (name, email, message, datetime.datetime.now()))
    
    message_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return message_id

def init_database():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contact_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()
