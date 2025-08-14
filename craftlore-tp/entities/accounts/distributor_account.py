#!/usr/bin/env python3
"""
Distributor account entity for CraftLore Account TP.
"""

from typing import Dict, List
from .base_account import BaseAccount
from core.enums import AccountType


class DistributorAccount(BaseAccount):
    """Distributor account for logistics and distribution services."""

    def __init__(self, account_id: str, public_key: str, email: str, timestamp):
        super().__init__(account_id, public_key, email, AccountType.DISTRIBUTOR, timestamp)

        # Distributor-specific properties (privacy-safe business data)
        self.distribution_type = ""  # "regional", "national", "international"
        self.service_regions = []  # Geographic coverage areas
        self.transportation_methods = []  # "road", "air", "sea"
        self.logistics_specializations = []  # "handicrafts", "textiles", "artwork"
        
        # Connected entities (using public keys)
        self.shipments_managed = []
        self.products_handled = []
        self.workshops_served = []
        self.wholesalers_delivered_to = []
        self.warehouse_facilities = []
        self.inventory_managed = []
        
        # Logistics metrics (privacy-safe)
        self.logistics_metrics = {
            'on_time_delivery_rate': 0.0,
            'damage_rate': 0.0,
            'customer_satisfaction': 0.0,
            'carbon_footprint_score': 0.0
        }
    
    def to_dict(self) -> Dict:
        data = super().to_dict()
        data.update({
            'distribution_type': self.distribution_type,
            'service_regions': self.service_regions,
            'transportation_methods': self.transportation_methods,
            'logistics_specializations': self.logistics_specializations,
            'shipments_managed': self.shipments_managed,
            'products_handled': self.products_handled,
            'workshops_served': self.workshops_served,
            'wholesalers_delivered_to': self.wholesalers_delivered_to,
            'warehouse_facilities': self.warehouse_facilities,
            'inventory_managed': self.inventory_managed,
            'logistics_metrics': self.logistics_metrics
        })
        return data
