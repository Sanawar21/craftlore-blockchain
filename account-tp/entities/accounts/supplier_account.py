#!/usr/bin/env python3
"""
Artisan account entity for CraftLore Account TP.
"""

from typing import Dict, List
from .base_account import BaseAccount
from core.enums import AccountType


class SupplierAccount(BaseAccount):
    """Supplier account for handicraft creators with detailed craft tracking."""
    
    def __init__(self, account_id: str, public_key: str, email: str, timestamp):
        super().__init__(account_id, public_key, email, AccountType.SUPPLIER, timestamp)
        self.raw_materials_supplied = []
        self.supplier_type = ""
        self.location = ""


    def to_dict(self) -> Dict:
        data = super().to_dict()
        data.update({
            'raw_materials_supplied': self.raw_materials_supplied,
            'supplier_type': self.supplier_type,
            'location': self.location
        })
        return data
