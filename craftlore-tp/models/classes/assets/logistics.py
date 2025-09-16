#!/usr/bin/env python3
"""
Logistics asset entity for CraftLore Account TP.
"""

from pydantic import Field
from typing import List, Optional
from . import BaseAsset
from models.enums import AssetType

class Logistics(BaseAsset):
    """Represents the movement of packaged goods through the supply chain."""
    asset_type: AssetType = Field(default=AssetType.LOGISTICS)
    transaction: str                 # Link to transfer transaction UID

    # Links
    assets: List[str]             # One or more packaging assets being shipped

    # Transport details
    carrier: str                         # e.g., "DHL", "FedEx", "Local Courier"
    tracking_id: Optional[str] = None    # Courier/Shipping company tracking number

    # Route
    origin: str                          # Pickup location
    destination: str                     # Final delivery location
    recipient: str         # Recipient's account public key
    transit_points: List[str] = Field(default_factory=list)  # e.g., ports, warehouses

    # Dates
    dispatch_date: str
    estimated_delivery_date: str = Field(default_factory=str)

    # Financials
    freight_cost_usd: Optional[float] = None
    insurance_details: Optional[dict] = Field(default_factory=dict)

    @property
    def forbidden_fields(self) :
        """Fields that should not be set during creation."""
        return super().forbidden_fields
