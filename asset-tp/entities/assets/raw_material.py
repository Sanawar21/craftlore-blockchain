#!/usr/bin/env python3
"""
Admin account entity for CraftLore Account TP.
"""

from typing import Dict, List
from .base_asset import BaseAsset
from core.enums import AssetType


class RawMaterial(BaseAsset):
    """Raw material asset for CraftLore."""

    def __init__(self, asset_id: str, public_key: str, timestamp):
        super().__init__(asset_id, public_key, AssetType.RAW_MATERIAL, timestamp)
        self.material_type = ""  # e.g., "wool", "cotton", "silk"
        self.supplier_id = ""
        self.quantity = 0  # Quantity in standard units (e.g., kg, meters)
        self.quantity_unit = ""
        self.processor_id = ""  # Workshop or artisan that processes this raw material
        self.harvested_date = ""
        self.source_location = ""
        self.batches_used_in = []  # List of product batches that used this raw material
        self.transaction_date = ""
    
    def to_dict(self) -> Dict:
        data = super().to_dict()
        data.update({
            'material_type': self.material_type,
            'supplier_id': self.supplier_id,
            'quantity': self.quantity,
            'quantity_unit': self.quantity_unit,
            'processor_id': self.processor_id,
            'harvested_date': self.harvested_date,
            'source_location': self.source_location,
            'batches_used_in': self.batches_used_in,
            'transaction_date': self.transaction_date
        })
        return data

    @property
    def unedited_fields(self) -> List[str]:
        """Fields that cannot be edited after creation."""
        fields = super().uneditable_fields
        fields.extend([
            "transaction_date", "batches_used_in"
        ])
        return fields

    @property
    def post_lock_fields(self) -> List[str]:
        """Fields that can be edited after the raw material is locked."""
        return ['material_type', 'supplier_id', 'quantity', 'quantity_unit', 
                'processor_id', 'harvested_date', 'source_location']