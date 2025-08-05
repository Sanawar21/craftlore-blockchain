#!/usr/bin/env python3
"""
Verifier account entity for CraftLore Account TP.
"""

from typing import Dict, List
from .base_account import BaseAccount
from core.enums import AccountType


class VerifierAccount(BaseAccount):
    """Verifier account for certification and authentication services."""
    
    def __init__(self, account_id: str, public_key: str, email: str, timestamp):
        super().__init__(account_id, public_key, email, AccountType.VERIFIER, timestamp)
        
        # Verifier-specific properties (privacy-safe professional data)
        self.certification_level = ""  # "expert", "master", "certified_assessor"
        self.verification_specializations = []  # "pashmina", "papier_mache", "carpet_weaving"
        self.credentials = []  # Professional credentials and qualifications
        self.years_experience = 0  # Professional background
        self.authorized_certifications = []  # Types of certificates they can issue
        
        # Connected entities (using public keys)
        self.verified_products = []
        self.verification_history = []
        self.issued_certificates = []
        self.quality_reports_created = []
        self.active_assignments = []
        
        # Verification metrics (privacy-safe)
        self.verification_metrics = {
            'accuracy_rating': 0.0,
            'reliability_score': 0.0,
            'certifications_issued': 0,
            'peer_recognition': 0.0
        }
    
    def to_dict(self) -> Dict:
        data = super().to_dict()
        data.update({
            'certification_level': self.certification_level,
            'verification_specializations': self.verification_specializations,
            'credentials': self.credentials,
            'years_experience': self.years_experience,
            'authorized_certifications': self.authorized_certifications,
            'verified_products': self.verified_products,
            'verification_history': self.verification_history,
            'issued_certificates': self.issued_certificates,
            'quality_reports_created': self.quality_reports_created,
            'active_assignments': self.active_assignments,
            'verification_metrics': self.verification_metrics
        })
        return data
