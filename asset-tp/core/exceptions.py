#!/usr/bin/env python3
"""
Core exceptions for CraftLore Account TP.
"""


class AssetError(Exception):
    """Base exception for asset-related errors."""
    pass


class AuthenticationError(AssetError):
    """Exception for authentication-related errors."""
    pass


class ValidationError(AssetError):
    """Exception for validation errors."""
    pass


class PermissionError(AssetError):
    """Exception for permission-related errors."""
    pass
