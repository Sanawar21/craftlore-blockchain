#!/usr/bin/env python3
"""
Core enumerations for CraftLore Account TP.
"""

from enum import Enum


class AssetType(Enum):
    """All supported asset types in CraftLore system."""
    RAW_MATERIAL = "raw_material"
    PRODUCT = "product"
    BATCH = "batch"
    PRODUCT_BATCH = "product_batch"
    WORK_ORDER = "work_order"
    
class WorkOrderStatus(Enum):
    """Status of a work order."""
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

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
