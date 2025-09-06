#!/usr/bin/env python3
"""
Batch asset entity for CraftLore Account TP.
"""

from pydantic import Field
from typing import List, Optional

from . import BaseAsset
from models.enums import AssetType, WorkOrderStatus, BatchStatus

# --- Product Batch ---
class ProductBatch(BaseAsset):
    """Represents a group of products produced together."""
    asset_type: AssetType = Field(default=AssetType.PRODUCT_BATCH)
    producer: str                        # Artisan or workshop public key
    quantity: int
    unit: str                            # e.g. "pieces", "kg"

    product_description: str             # Free text (e.g., "100 wool shawls")
    specifications: List[str] = Field(default_factory=list)
    design_reference: str = Field(default_factory=str)
    special_instructions: str = Field(default_factory=str)
    status: BatchStatus = Field(default=BatchStatus.IN_PROGRESS)
    
    # Links
    work_order: Optional[str] = None  # If produced for a WorkOrder
    production_date: str = Field(default_factory=str)
    sub_assignees: List[str] = Field(default_factory=list)  # Other artisans involved