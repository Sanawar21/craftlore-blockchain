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
    WARRANTY = "warranty"


class AssetStatus(Enum):
    """Status of any asset."""
    AVAILABLE = "available"
    LOCKED = "locked"
    IN_TRANSIT = "in_transit"
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DELETED = "deleted"
    
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


class ProductBatchStatus(Enum):
    """Status of a product batch."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    LOCKED = "locked"
    DELIVERED = "delivered"


class CertificationStatus(Enum):
    """Quality certification status."""
    UNCERTIFIED = "uncertified"
    PENDING_CERTIFICATION = "pending_certification"
    CERTIFIED = "certified"
    REJECTED = "rejected"


class WarrantyStatus(Enum):
    """Warranty status."""
    ACTIVE = "active"
    EXPIRED = "expired"
    VOID = "void"
