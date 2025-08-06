# !/usr/bin/env python3


from typing import Dict, List
from .base_asset import BaseAsset
from core.enums import AssetType


class Product(BaseAsset):
    """Product asset for CraftLore."""
    
    def __init__(self, asset_id: str, public_key: str, timestamp):
        super().__init__(asset_id, public_key, AssetType.PRODUCT_BATCH, timestamp)
        self.batch_id = ""  # ID of the batch this product belongs to
        self.batch_index = 0
        self.current_owner_id = ""  # Current owner (could be a buyer or reseller)
        self.previous_owners = []  # List of previous owner IDs
        self.purchase_date = ""  # Date of purchase by current owner
        
        

    def to_dict(self) -> Dict:
        data = super().to_dict()
        data.update({
            'batch_id': self.batch_id,
            'seller_id': self.seller_id,
            'current_owner_id': self.current_owner_id,
            'previous_owners': self.previous_owners,
            'purchase_date': self.purchase_date
        })
        return data
