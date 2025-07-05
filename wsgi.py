#!/usr/bin/env python3
"""
WSGI configuration for Repository Analyzer Flask app
This file is used by PythonAnywhere to serve the application
"""

import sys
import os

# Add the project directory to the Python path
path = os.path.dirname(os.path.abspath(__file__))
if path not in sys.path:
    sys.path.append(path)

# Import the Flask app
from app import app as application

# For debugging purposes
if __name__ == "__main__":
    application.run() 