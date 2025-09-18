#!/usr/bin/env python3
"""
Base account entity for CraftLore Account TP.
"""

from pydantic import Field
from ...enums import  AccountType

from ..base_class import BaseClass

class BaseAccount(BaseClass):
    """Base account model for CraftLore Account TP."""
    public_key: str  # PRIMARY IDENTIFIER
    email: str   # ONLY personal data for off-chain linking
    account_type: AccountType
    assets: list = Field(default_factory=list)
    work_orders_issued: list = Field(default_factory=list)
    region: str = Field(default_factory=str)
    specializations: list = Field(default_factory=list)

    @property
    def forbidden_fields(self) :
        return super().forbidden_fields.union({
            "assets",
            "work_orders_issued",
        })

    @property
    def editable_fields(self) -> set:
        return super().editable_fields.union({
            "region",
            "specializations",
        })