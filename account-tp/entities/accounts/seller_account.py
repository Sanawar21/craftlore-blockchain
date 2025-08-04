#!/usr/bin/env python3
"""
Seller account entity for CraftLore Account TP.
"""

from typing import Dict, List
from .base_account import BaseAccount
from utils.enums import AccountType


class SellerAccount(BaseAccount):
    """Seller account for basic handicraft sellers."""
    
    def __init__(self, account_id: str, public_key: str, email: str):
        super().__init__(account_id, public_key, email, AccountType.SELLER)
        
        # Seller-specific properties (privacy-safe business data)
        self.business_name = ""
        self.business_type = ""  # "individual_artisan", "cooperative", "workshop"
        self.registration_number = ""  # Business registration
        self.product_categories = []  # Types of crafts sold
        
        # Connected entities (using public keys)
        self.products = []
        self.sales_history = []
        self.buyers_served = []
        self.certificates_held = []
        self.ratings = {
            'average': 0.0,
            'count': 0,
            'reviews': []
        }
    
    def to_dict(self) -> Dict:
        data = super().to_dict()
        data.update({
            'business_name': self.business_name,
            'business_type': self.business_type,
            'registration_number': self.registration_number,
            'product_categories': self.product_categories,
            'products': self.products,
            'sales_history': self.sales_history,
            'buyers_served': self.buyers_served,
            'certificates_held': self.certificates_held,
            'ratings': self.ratings
        })
        return data
