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

    @property
    def forbidden_fields(self) :
        """Fields that should not be set during creation."""
        return super().forbidden_fields.union({
            # base asset
            "transfer_logistics",
            "previous_owners",
        })

    @property
    def editable_fields(self) -> set:
        """Fields that can be edited after creation."""
        return super().editable_fields