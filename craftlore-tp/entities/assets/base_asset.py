#!/usr/bin/env python3
"""
Base account class for CraftLore Account TP.
"""

from typing import Dict, List, get_type_hints
from enum import Enum
from core.enums import AssetType, AuthenticationStatus, VerificationStatus, WorkOrderStatus, CertificationStatus, WarrantyStatus
import inspect

class BaseAsset:
    """Base class for all CraftLore assets with privacy-first design."""

    def __init__(self, asset_id: str, owner: str, asset_type: AssetType, timestamp):
        # Core identifiers
        self.asset_id = asset_id  # Human-readable reference
        self.owner = owner

        # Asset metadata
        self.asset_type = asset_type
        self.authentication_status = AuthenticationStatus.PENDING
        self.verification_status = VerificationStatus.UNVERIFIED
        
        # Privacy-safe professional data
        self.previous_owners = []  # List of public keys of previous owners

        # Timestamps
        self.created_timestamp = timestamp
        self.updated_timestamp = timestamp

        # System metadata
        self.is_deleted = False
        self.history = []  # Audit trail
        
        # Connected entities (using public keys as identifiers)
        self.connected_entities = {}
        self.is_locked = False  # asset cannot be edited after being locked

        # Warranty and certification fields
        self.warranty_status = WarrantyStatus.ACTIVE
        self.warranty_expiry_date = ""
        self.warranty_registered_date = ""
        self.certification_status = CertificationStatus.UNCERTIFIED
        self.certification_details = {}
        self.repair_history = []  # List of repair records
        self.sustainability_scores = {}  # Environmental and compliance scores

    def to_dict(self) -> Dict:
        """Convert asset to dictionary for blockchain storage."""
        return {
            'asset_id': self.asset_id,
            'asset_type': self.asset_type.value,
            'authentication_status': self.authentication_status.value,
            'verification_status': self.verification_status.value,
            'owner': self.owner,
            'previous_owners': self.previous_owners,
            'created_timestamp': self.created_timestamp,
            'updated_timestamp': self.updated_timestamp,
            'is_deleted': self.is_deleted,
            'history': self.history,
            'connected_entities': self.connected_entities,
            'is_locked': self.is_locked,
            'warranty_status': self.warranty_status.value,
            'warranty_expiry_date': self.warranty_expiry_date,
            'warranty_registered_date': self.warranty_registered_date,
            'certification_status': self.certification_status.value,
            'certification_details': self.certification_details,
            'repair_history': self.repair_history,
            'sustainability_scores': self.sustainability_scores
        }
    
    @property
    def uneditable_fields(self) -> List[str]:
        """Fields that are read-only and cannot be directly modified in 'asset_edit' transaction."""
        return ['asset_id', 'created_timestamp',
                'updated_timestamp', 'history', 'is_deleted',
                'connected_entities', 'is_locked', 'asset_type',
                'authentication_status', 'verification_status',
                'previous_owners', 'owner', 'is_locked']

    @property
    def post_lock_editable_fields(self) -> List[str]:
        """Fields that can be changed after asset is locked."""
        return ['owner', 'previous_owners']


    @classmethod
    def from_dict(cls, data: Dict):
        """Dynamically create instance from dictionary, including Enums and subclass fields."""
        sig = inspect.signature(cls.__init__)
        type_hints = get_type_hints(cls.__init__)

        init_args = {}
        consumed_keys = set()

        for param in sig.parameters.values():
            if param.name == "self":
                continue

            if param.kind == inspect.Parameter.VAR_KEYWORD:
                continue  # handle later

            value = data.get(param.name)
            consumed_keys.add(param.name)

            expected_type = type_hints.get(param.name)
            if expected_type and isinstance(expected_type, type) and issubclass(expected_type, Enum):
                if isinstance(value, str):
                    value = expected_type(value)

            init_args[param.name] = value

        # Handle **kwargs: include all unmatched items
        extra_kwargs = {}
        if any(p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values()):
            for k, v in data.items():
                if k in consumed_keys:
                    continue
                extra_kwargs[k] = cls._convert_enum_value(v)

            init_args.update(extra_kwargs)

        # Instantiate
        instance = cls(**init_args)

        # Attach all fields from dict, converting enums if needed
        for key, value in data.items():
            setattr(instance, key, cls._convert_enum_value(value))

        return instance


    @staticmethod
    def _convert_enum_value(value):
        """Convert a string back into an Enum if it matches any known Enum type."""
        if isinstance(value, str):
            for enum_cls in Enum.__subclasses__():
                # Compare against enum member names
                if value in enum_cls.__members__:
                    return enum_cls[value]
                # Compare against enum member values
                for member in enum_cls:
                    if value == member.value:
                        return member
        return value

    

    def _convert_enum_fields(self, data: Dict):
        """Dynamically convert enum attributes (even if not in constructor)."""
        type_hints = get_type_hints(type(self))
        for key, expected_type in type_hints.items():
            if (
                key in data
                and isinstance(expected_type, type)
                and issubclass(expected_type, Enum)
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
