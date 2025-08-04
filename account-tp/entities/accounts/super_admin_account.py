#!/usr/bin/env python3
"""
Super Admin account entity for CraftLore Account TP.
"""

from typing import Dict, List
from .base_account import BaseAccount
from utils.enums import AccountType


class SuperAdminAccount(BaseAccount):
    """Super Admin account with full system access and control."""
    
    def __init__(self, account_id: str, public_key: str, email: str):
        super().__init__(account_id, public_key, email, AccountType.SUPER_ADMIN)
        
        # Super Admin-specific properties
        self.admin_level = "super_admin"
        self.permissions = [
            'full_system_access',
            'manage_admins',
            'system_configuration',
            'bootstrap_system',
            'emergency_actions',
            'audit_trail_access',
            'global_oversight'
        ]
        self.security_clearance = "maximum"
        self.emergency_contacts = []
        
        # Connected entities (using public keys)
        self.managed_admins = []
        self.system_configurations = []
        self.emergency_actions = []
        self.audit_trails = []
        self.global_reports = []
        
        # Super Admin metrics (privacy-safe)
        self.super_admin_metrics = {
            'system_uptime_managed': 0.0,
            'critical_issues_resolved': 0,
            'security_incidents_handled': 0,
            'system_performance_score': 0.0
        }
    
    def to_dict(self) -> Dict:
        data = super().to_dict()
        data.update({
            'admin_level': self.admin_level,
            'permissions': self.permissions,
            'security_clearance': self.security_clearance,
            'emergency_contacts': self.emergency_contacts,
            'managed_admins': self.managed_admins,
            'system_configurations': self.system_configurations,
            'emergency_actions': self.emergency_actions,
            'audit_trails': self.audit_trails,
            'global_reports': self.global_reports,
            'super_admin_metrics': self.super_admin_metrics
        })
        return data
