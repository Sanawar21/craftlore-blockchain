#!/usr/bin/env python3
"""
Base asset entity for CraftLore Account TP.
"""

from pydantic import Field
from ...enums import AssetType

from ..base_class import BaseClass



class BaseAsset(BaseClass):
    """Base asset model for CraftLore Account TP."""
    uid: str  # PRIMARY IDENTIFIER
    asset_owner: str
    asset_type: AssetType
    transfer_logistics: list = Field(default_factory=list)
    previous_owners: list = Field(default_factory=list)