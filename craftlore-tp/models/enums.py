from enum import Enum

class AuthenticationStatus(Enum):
    """Accounts authentication status"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class AccountType(Enum):
    SUPPLIER = "supplier"

class EventType(Enum):
    ACCOUNT_CREATED = "account_created"
    ACCOUNT_UPDATED = "account_updated"
    ACCOUNT_DELETED = "account_deleted"