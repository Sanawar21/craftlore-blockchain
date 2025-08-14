#!/usr/bin/env python3
"""
Admin account entity for CraftLore Account TP.
"""

from typing import Dict, List
from .base_account import BaseAccount
from core.enums import AccountType


class AdminAccount(BaseAccount):
    """Admin account for system management and oversight."""
    
    def __init__(self, account_id: str, public_key: str, email: str, timestamp):
        super().__init__(account_id, public_key, email, AccountType.ADMIN, timestamp)

        # Admin-specific properties
        self.admin_level = ""  # "regional", "national", "specialist"
        self.permissions = [
            'authenticate_accounts',
            'manage_verifications',
            'handle_disputes',
            'generate_reports',
            'moderate_content'
        ]
        self.assigned_regions = []  # Geographic regions they manage
        self.specialization_areas = []  # Areas of administrative focus
        
        # Connected entities (using public keys)
        self.managed_accounts = []
        self.authentication_actions = []
        self.dispute_resolutions = []
        self.reports_generated = []
        self.system_actions = []
        
        # Admin metrics (privacy-safe)
        self.admin_metrics = {
            'accounts_authenticated': 0,
            'disputes_resolved': 0,
            'response_time_avg': 0.0,
            'user_satisfaction': 0.0
        }
    
    def to_dict(self) -> Dict:
        data = super().to_dict()
        data.update({
            'admin_level': self.admin_level,
            'permissions': self.permissions,
            'assigned_regions': self.assigned_regions,
            'specialization_areas': self.specialization_areas,
            'managed_accounts': self.managed_accounts,
            'authentication_actions': self.authentication_actions,
            'dispute_resolutions': self.dispute_resolutions,
            'reports_generated': self.reports_generated,
            'system_actions': self.system_actions,
            'admin_metrics': self.admin_metrics
        })
        return data

    @classmethod
    def from_dict(cls, data: Dict):
        """Create AdminAccount instance from dictionary."""
        # Use the base class from_dict method
        instance = super().from_dict(data)
        return instance
