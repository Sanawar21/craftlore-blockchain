from enum import Enum

class BaseEnum(str, Enum):
    """Base Enum class to ensure string values"""


class AuthenticationStatus(BaseEnum):
    """Accounts authentication status"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class AccountType(BaseEnum):
    SUPPLIER = "supplier"

class AssetType(BaseEnum):
    RAW_MATERIAL = "raw_material"

class EventType(BaseEnum):
    ACCOUNT_CREATED = "create/account"
    ACCOUNT_UPDATED = "update/account"
    ACCOUNT_DELETED = "delete/account"
    ASSET_CREATED = "create/asset"
    ASSET_UPDATED = "update/asset"
    ASSET_DELETED = "delete/asset"