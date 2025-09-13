#!/usr/bin/env python3
"""
Raw material asset entity for CraftLore Account TP.
"""

from pydantic import Field, BaseModel

from . import BaseAsset
from models.enums import AssetType
from typing import List, Optional

class UsageRecord(BaseModel):
    batch: str  # Product batch UID
    usage_quantity: float  # Quantity of raw material used in this batch
    raw_material: str

class RawMaterial(BaseAsset):
    """Raw material asset that is produced by suppliers and is used in batches."""
    asset_type: AssetType = Field(default=AssetType.RAW_MATERIAL)
    material_type: str  # e.g., "wool", "cotton", "silk"
    supplier: str = Field(default_factory=str)
    quantity: float  # Quantity in standard units (e.g., kg, meters)
    quantity_unit: str
    unit_price_usd: float  # Price per unit of quantity
    processor_public_key: Optional[str] = Field(default=None)    # Workshop or artisan that processes this raw material
    harvested_date: str 
    source_location: str = Field(default_factory=str)
    batches_used_in: List[UsageRecord] = Field(default_factory=list)  # List of product batches that used this raw material

