# api/index.py
# Entry point for Vercel Python serverless deployment

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app  # Import the Flask app from app.py

# Vercel looks for 'app' variable
# No need for if __name__ == '__main__' block
