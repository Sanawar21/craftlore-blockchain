#!/usr/bin/env python3
"""
Core exceptions for CraftLore Account TP.
"""


class AccountError(Exception):
    """Base exception for account-related errors."""
    pass


class AuthenticationError(AccountError):
    """Exception for authentication-related errors."""
    pass


class ValidationError(AccountError):
    """Exception for validation errors."""
    pass


class PermissionError(AccountError):
    """Exception for permission-related errors."""
    pass
