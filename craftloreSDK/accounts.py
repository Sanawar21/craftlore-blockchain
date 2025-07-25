#!/usr/bin/env python3
"""
Account classes for the CraftLore system implementing role-based access control.
"""

from object import CraftloreObject, AccountType, AuthenticationStatus, Permission
from typing import Set, List
import time

class Account(CraftloreObject):
    """Base class for all account types in the CraftLore system."""
    
    def __init__(self, **kwargs):
        # Account-specific attributes (before calling super().__init__)
        self.account_id = kwargs.get('account_id', self.generate_unique_identifier())
        self.account_type = kwargs.get('account_type', AccountType.BUYER)
        self.permissions: Set[Permission] = set(kwargs.get('permissions', []))
        self.email = kwargs.get('email', '')
        self.phone = kwargs.get('phone', '')
        self.address = kwargs.get('address', '')
        self.is_active = kwargs.get('is_active', True)
        
        # Remove these from kwargs to avoid conflicts
        kwargs_copy = kwargs.copy()
        for key in ['account_id', 'account_type', 'permissions', 'email', 'phone', 'address', 'is_active']:
            kwargs_copy.pop(key, None)
        
        super().__init__(**kwargs_copy)
        
        # Set default permissions based on account type
        self._set_default_permissions()
    
    def _set_default_permissions(self):
        """Set default permissions based on account type."""
        if self.account_type == AccountType.SUPER_ADMIN:
            self.permissions = {perm for perm in Permission}
        elif self.account_type == AccountType.ARTISAN_ADMIN:
            self.permissions = {Permission.CREATE, Permission.READ, Permission.UPDATE, Permission.AUTHENTICATE}
        else:
            self.permissions = {Permission.READ}
    
    @property
    def identifier(self):
        return self.account_id
    
    @property
    def creator(self):
        return getattr(self, 'created_by', 'system')
    
    @property
    def type(self):
        return 'account'
    
    @property
    def owner(self):
        return self.account_id  # Accounts own themselves
    
    def has_permission(self, permission: Permission) -> bool:
        """Check if account has a specific permission."""
        return permission in self.permissions or Permission.SUPER_ADMIN in self.permissions

class SuperAdminAccount(Account):
    """Super administrator account with full system access."""
    
    def __init__(self, **kwargs):
        kwargs['account_type'] = AccountType.SUPER_ADMIN
        super().__init__(**kwargs)
        
        # Super admin specific attributes
        self.can_create_admins = True
        self.can_suspend_accounts = True
        self.system_access_level = 'full'

class ArtisanAdminAccount(Account):
    """Admin account for managing artisan accounts and artisan-related objects."""
    
    def __init__(self, **kwargs):
        kwargs['account_type'] = AccountType.ARTISAN_ADMIN
        super().__init__(**kwargs)
        
        # Artisan admin specific attributes
        self.region = kwargs.get('region', 'Kashmir')
        self.managed_artisans: List[str] = kwargs.get('managed_artisans', [])
        self.craft_specialization = kwargs.get('craft_specialization', 'all')

class ArtisanAccount(Account):
    """Account for artisans (craftspeople)."""
    
    def __init__(self, **kwargs):
        kwargs['account_type'] = AccountType.ARTISAN
        super().__init__(**kwargs)
        
        # Artisan specific attributes
        self.artisan_name = kwargs.get('artisan_name', '')
        self.specialization = kwargs.get('specialization', '')
        self.years_experience = kwargs.get('years_experience', 0)
        self.workshop_id = kwargs.get('workshop_id', '')
        self.certifications: List[str] = kwargs.get('certifications', [])
        self.payment_address = kwargs.get('payment_address', '')
        self.skill_level = kwargs.get('skill_level', 'beginner')  # beginner, intermediate, expert, master
        
        # Geographic information
        self.location = kwargs.get('location', '')
        self.region = kwargs.get('region', 'Kashmir')
        
        # Government identification
        self.govt_id = kwargs.get('govt_id', '')
        self.aadhaar_number = kwargs.get('aadhaar_number', '')

class SupplierAccount(Account):
    """Account for raw material suppliers."""
    
    def __init__(self, **kwargs):
        kwargs['account_type'] = AccountType.SUPPLIER
        super().__init__(**kwargs)
        
        # Supplier specific attributes
        self.business_name = kwargs.get('business_name', '')
        self.license_number = kwargs.get('license_number', '')
        self.material_types: List[str] = kwargs.get('material_types', [])
        self.certifications: List[str] = kwargs.get('certifications', [])
        self.supply_capacity = kwargs.get('supply_capacity', 0)

class WorkshopAccount(Account):
    """Account for manufacturing workshops."""
    
    def __init__(self, **kwargs):
        kwargs['account_type'] = AccountType.WORKSHOP
        super().__init__(**kwargs)
        
        # Workshop specific attributes
        self.workshop_name = kwargs.get('workshop_name', '')
        self.owner_name = kwargs.get('owner_name', '')
        self.craft_types: List[str] = kwargs.get('craft_types', [])
        self.number_of_artisans = kwargs.get('number_of_artisans', 0)
        self.production_capacity = kwargs.get('production_capacity', 0)
        self.certifications: List[str] = kwargs.get('certifications', [])

class BuyerAccount(Account):
    """Account for end customers/buyers."""
    
    def __init__(self, **kwargs):
        kwargs['account_type'] = AccountType.BUYER
        super().__init__(**kwargs)
        
        # Buyer specific attributes
        self.buyer_name = kwargs.get('buyer_name', '')
        self.preferences: List[str] = kwargs.get('preferences', [])
        self.purchase_history: List[str] = kwargs.get('purchase_history', [])
        self.wallet_address = kwargs.get('wallet_address', '')  # For NFT ownership

# Administrative account classes for other stakeholders
class SupplierAdminAccount(Account):
    """Admin account for managing supplier accounts."""
    
    def __init__(self, **kwargs):
        kwargs['account_type'] = AccountType.SUPPLIER_ADMIN
        super().__init__(**kwargs)

class WorkshopAdminAccount(Account):
    """Admin account for managing workshop accounts."""
    
    def __init__(self, **kwargs):
        kwargs['account_type'] = AccountType.WORKSHOP_ADMIN
        super().__init__(**kwargs)

class DistributorAdminAccount(Account):
    """Admin account for managing distributor accounts."""
    
    def __init__(self, **kwargs):
        kwargs['account_type'] = AccountType.DISTRIBUTOR_ADMIN
        super().__init__(**kwargs)

class WholesalerAdminAccount(Account):
    """Admin account for managing wholesaler accounts."""
    
    def __init__(self, **kwargs):
        kwargs['account_type'] = AccountType.WHOLESALER_ADMIN
        super().__init__(**kwargs)

class RetailerAdminAccount(Account):
    """Admin account for managing retailer accounts."""
    
    def __init__(self, **kwargs):
        kwargs['account_type'] = AccountType.RETAILER_ADMIN
        super().__init__(**kwargs)

# Regular stakeholder accounts
class DistributorAccount(Account):
    """Account for distributors."""
    
    def __init__(self, **kwargs):
        kwargs['account_type'] = AccountType.DISTRIBUTOR
        super().__init__(**kwargs)
        
        self.business_name = kwargs.get('business_name', '')
        self.distribution_regions: List[str] = kwargs.get('distribution_regions', [])

class WholesalerAccount(Account):
    """Account for wholesalers."""
    
    def __init__(self, **kwargs):
        kwargs['account_type'] = AccountType.WHOLESALER
        super().__init__(**kwargs)
        
        self.business_name = kwargs.get('business_name', '')
        self.wholesale_categories: List[str] = kwargs.get('wholesale_categories', [])

class RetailerAccount(Account):
    """Account for retailers."""
    
    def __init__(self, **kwargs):
        kwargs['account_type'] = AccountType.RETAILER
        super().__init__(**kwargs)
        
        self.business_name = kwargs.get('business_name', '')
        self.store_type = kwargs.get('store_type', 'physical')  # physical, online, both
        self.retail_categories: List[str] = kwargs.get('retail_categories', [])
