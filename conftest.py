"""
Pytest configuration – ensures project root is on sys.path
so that `from src.xxx import yyy` works from any test file.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
