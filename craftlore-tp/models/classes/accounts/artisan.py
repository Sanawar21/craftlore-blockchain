#!/usr/bin/env python3
"""
Artisan account entity for CraftLore Account TP.
"""

from pydantic import Field

from . import BaseAccount
from models.enums import AccountType, ArtisanSkillLevel

class ArtisanAccount(BaseAccount):
    """Artisan account that creates finished goods."""
    account_type: AccountType = Field(default=AccountType.ARTISAN)
    skill_level: ArtisanSkillLevel
    craft_categories: list = Field(default_factory=list)  # Types of crafts they create
    years_of_experience: int
    traditional_techniques: list = Field(default_factory=list)  # Traditional methods mastered
    work_orders_assigned: list = Field(default_factory=list)  # Work orders directly assigned to this artisan
    work_orders_accepted: list = Field(default_factory=list)  # Work orders accepted by this artisan
    work_orders_rejected: list = Field(default_factory=list)  # Work orders rejected by this artisan
    work_orders_sub_assigned: list = Field(default_factory=list)  # Work orders sub-assigned to this artisan by workshops
    workshops_worked_for: list = Field(default_factory=list)
    