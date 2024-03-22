# !/usr/bin/env python3

"""
Main entry point for the application.
"""

import sys
from qdata.app import Application

if __name__ == "__main__":
    app = Application(sys.argv)
    sys.exit(app.exec())
