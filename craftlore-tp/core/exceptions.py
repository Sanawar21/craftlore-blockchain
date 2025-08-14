#!/usr/bin/env python3
"""
Core exceptions for CraftLore Combined TP.
"""


class CraftLoreError(Exception):
    """Base exception for all CraftLore-related errors."""
    pass


class AccountError(CraftLoreError):
    """Base exception for account-related errors."""
    pass


class AssetError(CraftLoreError):
    """Base exception for asset-related errors."""
    pass


class AuthenticationError(CraftLoreError):
    """Exception for authentication-related errors."""
    pass


class ValidationError(CraftLoreError):
    """Exception for validation errors."""
    pass


class PermissionError(CraftLoreError):
    """Exception for permission-related errors."""
    pass


class TransferError(AssetError):
    """Exception for asset transfer errors."""
    pass


class WorkflowError(AssetError):
    """Exception for workflow-related errors."""
    pass
