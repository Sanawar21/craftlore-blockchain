#!/usr/bin/env python3
"""
Base account entity for CraftLore Account TP.
"""

from pydantic import BaseModel, Field
from ...enums import AuthenticationStatus, AccountType


class BaseAccount(BaseModel):
    """Base account model for CraftLore Account TP."""
    public_key: str  # PRIMARY IDENTIFIER
    email: str   # ONLY personal data for off-chain linking
    account_type: AccountType
    assets: list = Field(default_factory=list)
    authentication_status: AuthenticationStatus = AuthenticationStatus.PENDING
    work_orders_issued: list = Field(default_factory=list)
    region: str = Field(default_factory=str)
    specializations: list = Field(default_factory=list)
    certifications: list = Field(default_factory=list)
    created_timestamp: str = Field(default_factory=str)
    updated_timestamp: str = Field(default_factory=str)
    is_deleted: bool = False
    history: list = Field(default_factory=list)