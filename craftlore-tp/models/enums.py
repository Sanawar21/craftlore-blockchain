from enum import Enum

class AuthenticationStatus(Enum):
    """Accounts authentication status"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class AccountType(Enum):
    SUPPLIER = "supplier"

class AssetType(Enum):
    RAW_MATERIAL = "raw_material"

class EventType(Enum):
    ACCOUNT_CREATED = "create/account"
    ACCOUNT_UPDATED = "update/account"
    ACCOUNT_DELETED = "delete/account"
    ASSET_CREATED = "create/asset"
    ASSET_UPDATED = "update/asset"
    ASSET_DELETED = "delete/asset"