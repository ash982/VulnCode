# app.py: main application, import everything and run the application
from flask import Flask
from routes import app

if __name__ == '__main__':
    app.run(debug=True)