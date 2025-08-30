# !/usr/bin/env python3

# Every product belongs to a batch, which is a collection of identical products made together.
# One batch will only be owned by one account

from typing import Dict, List
from .base_asset import BaseAsset
from core.enums import AssetType

class Logistics(BaseAsset):
    """Logistics asset for CraftLore."""
    
    def __init__(self, asset_id: str, public_key: str, timestamp):
        super().__init__(asset_id, public_key, AssetType.LOGISTICS, timestamp)
        self.packages = []
        self.charges = {}
        self.routes = []
        self.carrier = ""
        self.dispatch_date = ""


    def to_dict(self) -> Dict:
        data = super().to_dict()
        data.update({
            'packages': self.packages,
            'charges': self.charges,
            'routes': self.routes,
            'carrier': self.carrier,
            'dispatch_date': self.dispatch_date
        })
        return data

