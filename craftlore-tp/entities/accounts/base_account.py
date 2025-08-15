#!/usr/bin/env python3
"""
Base account class for CraftLore Account TP.
"""

from typing import Dict, List, get_type_hints
from enum import Enum
import inspect
from core.enums import AccountType, AuthenticationStatus, VerificationStatus


class BaseAccount:
    """Base class for all CraftLore accounts with privacy-first design."""
    
    # Type annotations for proper enum conversion
    account_type: AccountType
    authentication_status: AuthenticationStatus
    verification_status: VerificationStatus
    
    def __init__(self, account_id: str, public_key: str, email: str, account_type: AccountType, timestamp):
        # Core identifiers - public_key is PRIMARY identifier
        self.account_id = account_id  # Human-readable reference
        self.public_key = public_key  # PRIMARY IDENTIFIER
        self.email = email  # ONLY personal data for off-chain linking
        
        # Account metadata
        self.account_type = account_type
        self.authentication_status = AuthenticationStatus.PENDING
        self.verification_status = VerificationStatus.UNVERIFIED
        
        # Privacy-safe professional data
        self.region = ""  # Generalized location only
        self.specialization = []  # Professional skills/focus areas
        self.certifications = []  # Professional certifications
        
        # Timestamps
        self.created_timestamp = timestamp
        self.updated_timestamp = timestamp

        # System metadata
        self.is_deleted = False
        self.history = []  # Audit trail
        
        # Connected entities (using public keys as identifiers)
        self.connected_entities = {}
        
        # Work orders issued by this account (available to all account types)
        self.work_orders_issued = []
    
    def to_dict(self) -> Dict:
        """Convert account to dictionary for blockchain storage."""
        return {
            'account_id': self.account_id,
            'public_key': self.public_key,
            'email': self.email,  # ONLY personal data stored
            'account_type': self.account_type.value,
            'authentication_status': self.authentication_status.value,
            'verification_status': self.verification_status.value,
            'region': self.region,
            'specialization': self.specialization,
            'certifications': self.certifications,
            'created_timestamp': self.created_timestamp,
            'updated_timestamp': self.updated_timestamp,
            'is_deleted': self.is_deleted,
            'history': self.history,
            'connected_entities': self.connected_entities,
            'work_orders_issued': self.work_orders_issued
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Dynamically create instance from dictionary, including Enums and subclass fields."""
        # Get the constructor signature for the specific class
        sig = inspect.signature(cls.__init__)
        type_hints = get_type_hints(cls.__init__)

        init_args = {}
        for param in sig.parameters.values():
            if param.name == 'self':
                continue

            value = data.get(param.name)
            expected_type = type_hints.get(param.name)

            # Automatically convert to Enum if needed
            if expected_type and isinstance(expected_type, type) and issubclass(expected_type, Enum):
                if isinstance(value, str):
                    value = expected_type(value)

            init_args[param.name] = value

        # Instantiate with converted and filtered args
        instance = cls(**init_args)

        # Set all other attributes from data (including those already initialized)
        for key, value in data.items():
            if key not in init_args:  # Only set attributes that weren't in constructor
                setattr(instance, key, value)

        # Convert other attributes with enums (outside constructor)
        instance._convert_enum_fields(data)

        return instance

    def _convert_enum_fields(self, data: Dict):
        """Dynamically convert enum attributes (even if not in constructor)."""
        # Get type hints from the actual instance class
        type_hints = get_type_hints(type(self))
        for key, expected_type in type_hints.items():
            if (
                key in data
                and isinstance(expected_type, type)
                and issubclass(expected_type, Enum)
                and isinstance(data[key], str)
            ):
                try:
                    setattr(self, key, expected_type(data[key]))
                except ValueError:
                    pass  # Ignore invalid enums silently
    
    def add_connection(self, entity_type: str, entity_public_key: str):
        """Add connection to another entity."""
        if entity_type not in self.connected_entities:
            self.connected_entities[entity_type] = []
        
        if entity_public_key not in self.connected_entities[entity_type]:
            self.connected_entities[entity_type].append(entity_public_key)
    
    def remove_connection(self, entity_type: str, entity_public_key: str):
        """Remove connection to another entity."""
        if entity_type in self.connected_entities:
            if entity_public_key in self.connected_entities[entity_type]:
                self.connected_entities[entity_type].remove(entity_public_key)
    
    def get_connected_entities(self, entity_type: str) -> List[str]:
        """Get list of connected entity public keys by type."""
        return self.connected_entities.get(entity_type, [])
    
    def add_history_entry(self, entry: Dict, timestamp: str = None):
        """Add an entry to the account history."""
        if timestamp:
            entry['timestamp'] = timestamp
        self.history.append(entry)
        if timestamp:
            self.updated_timestamp = timestamp