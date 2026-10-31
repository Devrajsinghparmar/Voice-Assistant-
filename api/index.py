"""
Vercel Serverless Function entrypoint for Deva Voice Assistant.
Exports the Flask 'app' instance.
"""

import os
import sys

# Ensure root project directory is on sys.path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from server import app

# Required by Vercel's @vercel/python runtime
application = app
