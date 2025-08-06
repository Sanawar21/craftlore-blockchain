# !/usr/bin/env python3

# Every product belongs to a batch, which is a collection of identical products made together.
# One batch will only be owned by one account

from typing import Dict, List
from .base_asset import BaseAsset
from core.enums import AssetType


class ProductBatch(BaseAsset):
    """Product batch asset for CraftLore."""
    
    def __init__(self, asset_id: str, public_key: str, timestamp):
        super().__init__(asset_id, public_key, AssetType.PRODUCT_BATCH, timestamp)
        self.raw_materials_used = []  # List of raw material IDs used in this batch
        self.initial_quantity = 0  # Total number of products in this batch
        self.quantity_unit = ""  # Unit of measurement (e.g., "pieces", "
        self.producer_id = ""  # Workshop or artisan that produced this batch
        self.production_date = ""  # Date when the batch was produced
        self.source_location = ""  # Location where the batch was produced
        self.category = ""
        self.artisans_involved = []
        self.current_quantity = 0
        self.reviews = []
        self.name = ""
        self.description = ""
        self.is_complete = False  # Whether the batch production is complete
        self.work_order_id = ""  # Work order that initiated this batch production

    def to_dict(self) -> Dict:
        data = super().to_dict()
        data.update({
            'raw_materials_used': self.raw_materials_used,
            'initial_quantity': self.initial_quantity,
            'quantity_unit': self.quantity_unit,
            'producer_id': self.producer_id,
            'production_date': self.production_date,
            'source_location': self.source_location,
            'category': self.category,
            'artisans_involved': self.artisans_involved,
            'current_quantity': self.current_quantity,
            'reviews': self.reviews,
            'name': self.name,
            'description': self.description,
            'is_complete': self.is_complete,
            'work_order_id': self.work_order_id
        })
        return data
