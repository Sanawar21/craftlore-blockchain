#!/usr/bin/env python3
"""Packaging is created when a batch of products has been completed (by work order or directly).
To get the products ready for shipment, they are packaged into a packaging asset. This may include products from other batches"""



from pydantic import Field
from typing import List, Optional

from . import BaseAsset
from models.enums import AssetType, WorkOrderStatus, BatchStatus

# --- Packaging ---
class Packaging(BaseAsset):
    """Represents a packaging asset for products ready for shipment."""
    asset_type: AssetType = Field(default=AssetType.PACKAGING)
    products: List[str]   # List of product ids included in this packaging
    package_type: str
    price_usd: float
    materials_used: List[str] = Field(default_factory=list)
    labelling: dict = Field(default_factory=dict)
    seal_id: str
    net_weight: float
    gross_weight: float
    package_width: float
    package_height: float

    @property
    def forbidden_fields(self) :
        """Fields that should not be set during creation."""
        return super().forbidden_fields
    
    @property
    def editable_fields(self) -> set:
        """Fields that can be edited after creation."""
        return super().editable_fields