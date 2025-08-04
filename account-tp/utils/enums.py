#!/usr/bin/env python3
"""
Core enumerations for CraftLore Account TP.
"""

from enum import Enum


class AccountType(Enum):
    """All supported account types in CraftLore system."""
    BUYER = "buyer"
    SELLER = "seller"
    ARTISAN = "artisan"
    WORKSHOP = "workshop"
    DISTRIBUTOR = "distributor"
    WHOLESALER = "wholesaler"
    RETAILER = "retailer"
    VERIFIER = "verifier"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


class AuthenticationStatus(Enum):
    """Account authentication status."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class VerificationStatus(Enum):
    """Account verification status."""
    UNVERIFIED = "unverified"
    VERIFIED = "verified"
    SUSPENDED = "suspended"
