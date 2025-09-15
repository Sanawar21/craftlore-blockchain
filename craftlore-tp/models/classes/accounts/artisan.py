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
    work_orders_completed: list = Field(default_factory=list)  # Work orders completed by this artisan
    sub_assignments: list = Field(default_factory=list)  # Sub-assignments assigned to this artisan
    sub_assignments_accepted: list = Field(default_factory=list)  # Sub-assignments accepted by this artisan
    sub_assignments_rejected: list = Field(default_factory=list)  # Sub-assignments rejected by this artisan
