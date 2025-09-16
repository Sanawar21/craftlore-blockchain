#!/usr/bin/env python3
"""
Batch asset entity for CraftLore Account TP.
"""

from pydantic import Field
from typing import List, Optional

from . import BaseAsset
from models.enums import AssetType, WorkOrderStatus, BatchStatus
from .raw_material import UsageRecord

# --- Product Batch ---
class ProductBatch(BaseAsset):
    """Represents a group of products produced together."""
    asset_type: AssetType = Field(default=AssetType.PRODUCT_BATCH)
    producer: str                        # Artisan or workshop public key
    quantity: float                     # Quantity of items planned for production; can change after completion
    raw_materials: List[UsageRecord] = Field(default_factory=list)  # List of raw material usage records for this batch
    unit: str                            # e.g. "pieces", "kg"
    units_produced: Optional[float] = None  # Amount of individual products produced after the batch is completed 

    product_description: str             # Free text (e.g., "100 wool shawls")
    specifications: List[str] = Field(default_factory=list)
    design_reference: str = Field(default_factory=str)
    special_instructions: str = Field(default_factory=str)
    status: BatchStatus = Field(default=BatchStatus.IN_PROGRESS)
    
    # Links
    work_order: Optional[str] = None  # If produced for a WorkOrder
    production_date: str = Field(default_factory=str)
    sub_assignments: List[str] = Field(default_factory=list)  # Sub-assignments of other artisans for this batch

    @property
    def forbidden_fields(self) :
        """Fields that should not be set during creation."""
        return super().forbidden_fields.union({
            # product batch
            "raw_materials"
            "units_produced",
            "status",
            "production_date",
            "sub_assignments",
        })