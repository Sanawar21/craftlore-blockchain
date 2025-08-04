#!/usr/bin/env python3
"""
Wholesaler account entity for CraftLore Account TP.
"""

from typing import Dict, List
from .base_account import BaseAccount
from utils.enums import AccountType


class WholesalerAccount(BaseAccount):
    """Wholesaler account for bulk handicraft trading."""
    
    def __init__(self, account_id: str, public_key: str, email: str):
        super().__init__(account_id, public_key, email, AccountType.WHOLESALER)
        
        # Wholesaler-specific properties (privacy-safe business data)
        self.business_type = ""  # "handicraft_wholesaler", "textile_distributor"
        self.market_focus = []  # "domestic", "export", "tourism"
        self.product_categories = []  # "carpets", "shawls", "artwork"
        self.trade_specialization = ""  # "bulk_orders", "retail_supply", "export"
        
        # Connected entities (using public keys)
        self.bulk_orders_placed = []
        self.products_purchased = []
        self.distributors_used = []
        self.retailers_sold_to = []
        self.inventory_records = []
        self.business_transactions = []
        
        # Trade metrics (privacy-safe)
        self.trade_metrics = {
            'monthly_volume': 0,
            'profit_margin_average': 0.0,
            'retailer_satisfaction': 0.0,
            'inventory_turnover': 0.0
        }
    
    def to_dict(self) -> Dict:
        data = super().to_dict()
        data.update({
            'business_type': self.business_type,
            'market_focus': self.market_focus,
            'product_categories': self.product_categories,
            'trade_specialization': self.trade_specialization,
            'bulk_orders_placed': self.bulk_orders_placed,
            'products_purchased': self.products_purchased,
            'distributors_used': self.distributors_used,
            'retailers_sold_to': self.retailers_sold_to,
            'inventory_records': self.inventory_records,
            'business_transactions': self.business_transactions,
            'trade_metrics': self.trade_metrics
        })
        return data
