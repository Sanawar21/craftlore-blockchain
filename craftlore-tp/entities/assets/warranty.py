#!/usr/bin/env python3
"""
Warranty asset for CraftLore.
"""

from typing import Dict, List
from .base_asset import BaseAsset
from core.enums import AssetType, WarrantyStatus


class Warranty(BaseAsset):
    """Warranty asset for CraftLore products."""
    
    def __init__(self, asset_id: str, public_key: str, timestamp):
        super().__init__(asset_id, public_key, AssetType.WARRANTY, timestamp)
        self.product_id = ""  # ID of the product this warranty covers
        self.buyer_id = ""  # ID of the buyer who registered the warranty
        self.warranty_period_months = 12  # Warranty period in months
        self.warranty_terms = ""  # Terms and conditions
        self.coverage_details = {}  # What is covered
        self.claim_history = []  # List of warranty claims

    def to_dict(self) -> Dict:
        data = super().to_dict()
        data.update({
            'product_id': self.product_id,
            'buyer_id': self.buyer_id,
            'warranty_period_months': self.warranty_period_months,
            'warranty_terms': self.warranty_terms,
            'coverage_details': self.coverage_details,
            'claim_history': self.claim_history
        })
        return data

    @property
    def uneditable_fields(self) -> List[str]:
        fields = super().uneditable_fields
        fields.extend([
            "product_id", "buyer_id", "warranty_period_months"
        ])
        return fields
    
    @property
    def post_lock_editable_fields(self) -> List[str]:
        fields = super().post_lock_editable_fields
        fields.extend([
            "claim_history", "warranty_status"
        ])
        return fields
