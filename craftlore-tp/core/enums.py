#!/usr/bin/env python3
"""
Core enumerations for CraftLore Combined TP.
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
    SUPPLIER = "supplier"


class AssetType(Enum):
    """All supported asset types in CraftLore system."""
    RAW_MATERIAL = "raw_material"
    PRODUCT = "product"
    PRODUCT_BATCH = "product_batch"
    WORK_ORDER = "work_order"
    WARRANTY = "warranty"
    PACKAGING = "packaging"
    LOGISTICS = "logistics"


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
