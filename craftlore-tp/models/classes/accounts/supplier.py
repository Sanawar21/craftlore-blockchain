#!/usr/bin/env python3
"""
Artisan account entity for CraftLore Account TP.
"""

from pydantic import Field

from . import BaseAccount
from models.enums import AccountType

class SupplierAccount(BaseAccount):
    """Supplier account that sources raw materials."""
    account_type: AccountType = Field(default=AccountType.SUPPLIER)
    raw_materials_supplied: list = Field(default_factory=list)
    raw_materials_created: list = Field(default_factory=list)
    supplier_type: str = Field(default_factory=str)

    
