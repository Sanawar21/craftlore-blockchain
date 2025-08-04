#!/usr/bin/env python3
"""
Workshop account entity for CraftLore Account TP.
"""

from typing import Dict, List
from .base_account import BaseAccount
from utils.enums import AccountType


class WorkshopAccount(BaseAccount):
    """Workshop account for craft production facilities."""
    
    def __init__(self, account_id: str, public_key: str, email: str):
        super().__init__(account_id, public_key, email, AccountType.WORKSHOP)
        
        # Workshop-specific properties (privacy-safe business data)
        self.workshop_type = ""  # "traditional_weaving", "carpet_making"
        self.craft_specializations = []  # Types of crafts produced
        self.capacity_artisans = 0  # Number of artisans (no personal details)
        self.production_capacity = ""  # "small", "medium", "large"
        self.traditional_methods = []  # Traditional techniques preserved
        
        # Connected entities (using public keys)
        self.employed_artisans = []
        self.work_orders_issued = []
        self.products_produced = []
        self.raw_materials_received = []
        self.suppliers = []
        self.distributors = []
        self.product_batches = []
        self.quality_reports_issued = []
        self.sustainability_metrics = []
        self.fair_trade_reports = []
        
        # Production metrics (privacy-safe aggregates)
        self.production_metrics = {
            'monthly_output': 0,
            'quality_average': 0.0,
            'on_time_delivery': 0.0,
            'sustainability_score': 0.0
        }
    
    def to_dict(self) -> Dict:
        data = super().to_dict()
        data.update({
            'workshop_type': self.workshop_type,
            'craft_specializations': self.craft_specializations,
            'capacity_artisans': self.capacity_artisans,
            'production_capacity': self.production_capacity,
            'traditional_methods': self.traditional_methods,
            'employed_artisans': self.employed_artisans,
            'work_orders_issued': self.work_orders_issued,
            'products_produced': self.products_produced,
            'raw_materials_received': self.raw_materials_received,
            'suppliers': self.suppliers,
            'distributors': self.distributors,
            'product_batches': self.product_batches,
            'quality_reports_issued': self.quality_reports_issued,
            'sustainability_metrics': self.sustainability_metrics,
            'fair_trade_reports': self.fair_trade_reports,
            'production_metrics': self.production_metrics
        })
        return data
