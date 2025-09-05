#!/usr/bin/env python3
"""
Base asset entity for CraftLore Account TP.
"""

from pydantic import BaseModel, Field, ConfigDict
from ...enums import AuthenticationStatus, AssetType
from abc import ABC


class BaseAsset(BaseModel, ABC):
    """Base asset model for CraftLore Account TP."""
    model_config = ConfigDict(use_enum_values=True)
    uid: str  # PRIMARY IDENTIFIER
    asset_owner: str
    asset_type: AssetType
    previous_owners: list = Field(default_factory=list)
    authentication_status: AuthenticationStatus = AuthenticationStatus.PENDING
    certifications: list = Field(default_factory=list)
    created_timestamp: str = Field(default_factory=str)
    updated_timestamp: str = Field(default_factory=str)
    is_deleted: bool = False
    history: list = Field(default_factory=list)