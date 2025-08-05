#!/usr/bin/env python3
"""
Buyer account entity for CraftLore Account TP.
"""

from typing import Dict, List
from .base_account import BaseAccount
from utils.enums import AccountType


class BuyerAccount(BaseAccount):
    """Buyer account for customers purchasing handicrafts."""
    
    def __init__(self, account_id: str, public_key: str, email: str, timestamp):
        super().__init__(account_id, public_key, email, AccountType.BUYER, timestamp)
        
        # Buyer-specific properties (privacy-safe)
        self.buyer_type = ""  # "individual_collector", "corporate_buyer", "tourist"
        self.purchase_interests = []  # "carpets", "shawls", "artwork"
        
        # Connected entities (using public keys)
        self.products_owned = []
        self.purchase_transactions = []
        self.retailers_purchased_from = []
        self.reviews_written = []
        self.warranty_records = []
        self.resale_transactions = []
    
    def to_dict(self) -> Dict:
        data = super().to_dict()
        data.update({
            'buyer_type': self.buyer_type,
            'purchase_interests': self.purchase_interests,
            'products_owned': self.products_owned,
            'purchase_transactions': self.purchase_transactions,
            'retailers_purchased_from': self.retailers_purchased_from,
            'reviews_written': self.reviews_written,
            'warranty_records': self.warranty_records,
            'resale_transactions': self.resale_transactions
        })
        return data
