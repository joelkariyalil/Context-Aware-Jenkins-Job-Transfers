"""
Configuration module for sharing Jenkins connection objects across test modules.
These connections are initialized in test_servers.py and used throughout the test suite.
"""

productionConn = None
interimConn = None
