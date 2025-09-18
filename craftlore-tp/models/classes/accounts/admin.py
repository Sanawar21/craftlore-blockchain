#!/usr/bin/env python3
"""
Admin account entity for CraftLore Account TP.
"""

from pydantic import Field

from . import BaseAccount
from models.enums import AccountType, AdminPermissionLevel, AdminAccountStatus
from typing import List

class AdminAccount(BaseAccount):
    """Admin account that manages the platform."""
    account_type: AccountType = Field(default=AccountType.ADMIN)
    permission_level: AdminPermissionLevel = Field(default=AdminPermissionLevel.MODERATOR)
    actions: List[str] = Field(default_factory=list)  # Transaction signatures of actions taken by this admin
    status: AdminAccountStatus = Field(default=AdminAccountStatus.ACTIVE)

    @property
    def forbidden_fields(self) :
        return super().forbidden_fields
    
    @property
    def editable_fields(self) -> set:
        return super().editable_fields