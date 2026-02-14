"""
Utils package initialization.
Exports utility functions for easy importing.
"""
from app.utils.audit import log_audit, get_audit_logs

__all__ = ['log_audit', 'get_audit_logs']
