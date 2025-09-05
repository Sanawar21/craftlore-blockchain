#!/usr/bin/env python3
"""
Work order asset entity for CraftLore Account TP.
"""

from pydantic import Field
from typing import List

from . import BaseAsset
from models.enums import AssetType, WorkOrderStatus, WorkOrderType

class WorkOrder(BaseAsset):
    """Work order asset that is provided to artisan and workshops for processing."""
    asset_type: AssetType = Field(default=AssetType.WORK_ORDER)
    assigner: str
    assignee: str  # Primary assignee (workshop or artisan)
    batch: str = Field(default_factory=str)  # Product batch this work order is for
    status: WorkOrderStatus = Field(default=WorkOrderStatus.PENDING)
    rejection_reason: str = Field(default_factory=str)
    work_type: WorkOrderType = Field(default=WorkOrderType.PRODUCTION)
    estimated_completion_date: str = Field(default_factory=str)
    completion_date: str = Field(default_factory=str)
    order_quantity: int  # Number of items/products requested in this work order
    sub_assignees: list = Field(default_factory=list)  # List of artisan public keys working on this order
    total_price: float  # Total price agreed for this work order

    # 🔽 New fields describing the "orderer's wants"
    product_description: str  # Free text: what exactly is requested
    specifications: List[str] = Field(default_factory=list)  # Structured specs (size, color, material, etc.)
    design_reference: str = Field(default_factory=str)  # Could be a URL, file hash, or ID for design docs
    special_instructions: str = Field(default_factory=str)  # Extra details, handling, packaging, etc.
