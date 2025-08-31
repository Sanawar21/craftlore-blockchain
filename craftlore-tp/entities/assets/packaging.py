# !/usr/bin/env python3

# Every product belongs to a batch, which is a collection of identical products made together.
# One batch will only be owned by one account

from typing import Dict, List
from .base_asset import BaseAsset
from core.enums import AssetType

class Packaging(BaseAsset):
    """Packaging asset for CraftLore."""
    
    def __init__(self, asset_id: str, owner: str, timestamp):
        super().__init__(asset_id, owner, AssetType.PACKAGING, timestamp)
        self.product_id = ""
        self.product_batch_id = ""
        self.product_batch_index = 0
        self.package_type = ""
        self.materials_used = []
        self.labelling = {}
        self.seal_id = ""
        self.net_weight = 0
        self.gross_weight = 0


    def to_dict(self) -> Dict:
        data = super().to_dict()
        data.update({
            'product_id': self.product_id,
            'product_batch_id': self.product_batch_id,
            'product_batch_index': self.product_batch_index,
            'package_type': self.package_type,
            'materials_used': self.materials_used,
            'labelling': self.labelling,
            'seal_id': self.seal_id,
            'net_weight': self.net_weight,
            'gross_weight': self.gross_weight
        })
        return data

