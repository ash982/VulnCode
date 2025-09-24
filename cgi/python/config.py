#!/usr/bin/env python3

import os

# Database configuration
DATABASE_PATH = '/var/www/data/app.db'

# Email settings
EMAIL_SETTINGS = {
    'smtp_server': 'localhost',
    'smtp_port': 587,
    'from_email': 'noreply@example.com'
}

# File upload settings
UPLOAD_DIR = '/var/www/data/uploads'
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Session settings
SESSION_DIR = '/var/www/data/sessions'
SESSION_TIMEOUT = 3600  # 1 hour
