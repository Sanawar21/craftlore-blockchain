#!/usr/bin/env python3
"""
Retailer account entity for CraftLore Account TP.
"""

from typing import Dict, List
from .base_account import BaseAccount
from utils.enums import AccountType


class RetailerAccount(BaseAccount):
    """Retailer account for direct-to-consumer handicraft sales."""
    
    def __init__(self, account_id: str, public_key: str, email: str, timestamp):
        super().__init__(account_id, public_key, email, AccountType.RETAILER, timestamp)
        
        # Retailer-specific properties (privacy-safe business data)
        self.retail_type = ""  # "physical_store", "online_marketplace", "exhibition"
        self.product_focus = []  # "traditional_crafts", "modern_designs"
        self.market_segment = ""  # "premium", "mid_range", "budget"
        self.sales_channels = []  # "in_store", "online", "exhibitions", "fairs"
        
        # Connected entities (using public keys)
        self.products_in_stock = []
        self.wholesalers_purchased_from = []
        self.buyers_sold_to = []
        self.business_transactions = []
        self.inventory_records = []
        
        # Retail metrics (privacy-safe)
        self.retail_metrics = {
            'monthly_sales': 0,
            'customer_satisfaction': 0.0,
            'inventory_turnover': 0.0,
            'return_rate': 0.0
        }
    
    def to_dict(self) -> Dict:
        data = super().to_dict()
        data.update({
            'retail_type': self.retail_type,
            'product_focus': self.product_focus,
            'market_segment': self.market_segment,
            'sales_channels': self.sales_channels,
            'products_in_stock': self.products_in_stock,
            'wholesalers_purchased_from': self.wholesalers_purchased_from,
            'buyers_sold_to': self.buyers_sold_to,
            'business_transactions': self.business_transactions,
            'inventory_records': self.inventory_records,
            'retail_metrics': self.retail_metrics
        })
        return data
