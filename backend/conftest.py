"""
Pytest global configuration and path setup.
Ensures `app` package is importable across all test environments.
"""

import sys
import os

# Add backend root directory (`C:\Users\altam\Desktop\upskill-recommender\backend`) to sys.path
backend_dir = os.path.abspath(os.path.dirname(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)
