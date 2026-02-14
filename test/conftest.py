"""
Pytest configuration and fixtures for tests.
"""
import pytest
import os
import sys

# Set test environment variables before any imports
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
os.environ['LOG_LEVEL'] = 'DEBUG'
os.environ['TESTING'] = 'true'
