#!/usr/bin/env python3
"""
Buyer account entity for CraftLore Account TP.
"""

from pydantic import Field

from . import BaseAccount
from models.enums import AccountType, ArtisanSkillLevel

class BuyerAccount(BaseAccount):
    """Buyer account that creates work orders or purchases products."""
    account_type: AccountType = Field(default=AccountType.BUYER)

    @property
    def forbidden_fields(self) :
        return super().forbidden_fields

    @property
    def editable_fields(self) -> set:
        return super().editable_fields