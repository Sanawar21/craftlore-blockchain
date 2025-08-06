#!/usr/bin/env python3
"""
Artisan account entity for CraftLore Account TP.
"""

from typing import Dict, List
from .base_account import BaseAccount
from core.enums import AccountType


class ArtisanAccount(BaseAccount):
    """Artisan account for handicraft creators with detailed craft tracking."""
    
    def __init__(self, account_id: str, public_key: str, email: str, timestamp):
        super().__init__(account_id, public_key, email, AccountType.ARTISAN, timestamp)
        
        # Artisan-specific properties (privacy-safe professional data)
        self.skill_level = ""  # "apprentice", "journeyman", "master_craftsman"
        self.craft_categories = []  # Types of crafts they create
        self.years_experience = 0  # Professional background metric
        self.traditional_techniques = []  # Traditional methods mastered
        
        self.work_orders_assigned = []
        self.workshops_worked_for = []
        self.payment_records = []
        self.skill_certificates = []
        self.work_progress_logs = []
        self.quality_reports_received = []
        self.fair_trade_reports = []
        self.repairs_performed = []
        self.product_assignments = []
        
        # Performance metrics (privacy-safe aggregates)
        self.performance_metrics = {
            'products_completed': 0,
            'average_quality_score': 0.0,
            'on_time_delivery_rate': 0.0,
            'customer_satisfaction': 0.0
        }
    
    def to_dict(self) -> Dict:
        data = super().to_dict()
        data.update({
            'skill_level': self.skill_level,
            'craft_categories': self.craft_categories,
            'years_experience': self.years_experience,
            'traditional_techniques': self.traditional_techniques,
            'products_created': self.products_created,
            'work_orders_assigned': self.work_orders_assigned,
            'workshops_worked_for': self.workshops_worked_for,
            'payment_records': self.payment_records,
            'skill_certificates': self.skill_certificates,
            'work_progress_logs': self.work_progress_logs,
            'quality_reports_received': self.quality_reports_received,
            'fair_trade_reports': self.fair_trade_reports,
            'repairs_performed': self.repairs_performed,
            'product_assignments': self.product_assignments,
            'performance_metrics': self.performance_metrics
        })
        return data
