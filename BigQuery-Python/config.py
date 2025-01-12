# config.py
import os

class Config:
    SECRET_KEY = "your_secret_key"  # Replace with a strong secret key
    GOOGLE_APPLICATION_CREDENTIALS = "path/to/your/service-account-file.json"
    SCHEMA_PATH = "schema.xml"
    USERS = {
        "customer": {"password": "customer123", "role": "customer"},
        "admin": {"password": "admin123", "role": "admin"}
    }
