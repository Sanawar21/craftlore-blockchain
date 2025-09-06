#!/usr/bin/env python3
"""
Work order asset entity for CraftLore Account TP.
"""

from pydantic import Field
from typing import List, Optional

from . import BaseAsset
from models.enums import AssetType, WorkOrderStatus, WorkOrderType


# --- Work Order ---
class WorkOrder(BaseAsset):
    """Contract between orderer and producer."""
    asset_type: AssetType = Field(default=AssetType.WORK_ORDER)
    assigner: str                        # Orderer account (supplier, retailer, etc.)
    assignee: str                        # Producer account (artisan or workshop)
    status: WorkOrderStatus = Field(default=WorkOrderStatus.PENDING)
    work_type: WorkOrderType = Field(default=WorkOrderType.PRODUCTION)
    batch: Optional[str] = None
    
    # Order details
    requested_quantity: int
    requested_quantity_unit: str                  # e.g. "pieces", "kg"
    product_description: str             # Free text (e.g., "100 wool shawls")
    specifications: List[str] = Field(default_factory=list)
    design_reference: str = Field(default_factory=str)
    special_instructions: str = Field(default_factory=str)

    # Contract details
    total_price_usd: float
    estimated_completion_date: str = Field(default_factory=str)
    completion_date: str = Field(default_factory=str)
    rejection_reason: str = Field(default_factory=str)

