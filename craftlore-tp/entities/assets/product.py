# !/usr/bin/env python3


from typing import Dict, List
from .base_asset import BaseAsset
from core.enums import AssetType


class Product(BaseAsset):
    """Product asset for CraftLore."""
    
    def __init__(self, asset_id: str, public_key: str, timestamp):
        super().__init__(asset_id, public_key, AssetType.PRODUCT, timestamp)
        self.batch_id = ""  # ID of the batch this product belongs to
        self.batch_index = 0
        self.purchase_date = ""  # Date of purchase by current owner
        self.is_locked = True
        self.resale_history = []  # List of resale transactions
        self.current_price = 0.0  # Current market price  
        

    def to_dict(self) -> Dict:
        data = super().to_dict()
        data.update({
            'batch_id': self.batch_id,
            'batch_index': self.batch_index,
            'purchase_date': self.purchase_date,
            'resale_history': self.resale_history,
            'current_price': self.current_price
        })
        return data
    
    @property
    def uneditable_fields(self) -> List[str]:
        """Fields that cannot be edited after creation."""
        fields = super().uneditable_fields
        fields.extend([
            'batch_id', 'batch_index', 'purchase_date'
        ])
        return fields
    
