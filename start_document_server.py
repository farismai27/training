#!/usr/bin/env python3
"""
Startup script for Document Management MCP Server
Run this with: python start_document_server.py
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import and run the server
from document_server import main
import asyncio

if __name__ == "__main__":
    asyncio.run(main())
