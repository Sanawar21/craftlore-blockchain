#!/usr/bin/env python3
"""
Base account class for CraftLore Account TP.
"""

from datetime import datetime
from typing import Dict, List
from utils.enums import AccountType, AuthenticationStatus, VerificationStatus


class BaseAccount:
    """Base class for all CraftLore accounts with privacy-first design."""
    
    def __init__(self, account_id: str, public_key: str, email: str, account_type: AccountType):
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
        self.created_timestamp = datetime.now().isoformat()
        self.updated_timestamp = datetime.now().isoformat()
        
        # System metadata
        self.is_deleted = False
        self.history = []  # Audit trail
        
        # Connected entities (using public keys as identifiers)
        self.connected_entities = {}
    
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
            'connected_entities': self.connected_entities
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Create account instance from dictionary."""
        account_type = AccountType(data['account_type'])
        instance = cls(
            account_id=data['account_id'],
            public_key=data['public_key'],
            email=data['email'],
            account_type=account_type
        )
        
        instance.authentication_status = AuthenticationStatus(data.get('authentication_status', 'pending'))
        instance.verification_status = VerificationStatus(data.get('verification_status', 'unverified'))
        instance.region = data.get('region', '')
        instance.specialization = data.get('specialization', [])
        instance.certifications = data.get('certifications', [])
        instance.created_timestamp = data.get('created_timestamp', datetime.now().isoformat())
        instance.updated_timestamp = data.get('updated_timestamp', datetime.now().isoformat())
        instance.is_deleted = data.get('is_deleted', False)
        instance.history = data.get('history', [])
        instance.connected_entities = data.get('connected_entities', {})
        
        return instance
    
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
