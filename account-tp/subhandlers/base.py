from abc import ABC, abstractmethod
from sawtooth_sdk.processor.context import Context
from sawtooth_sdk.processor.exceptions import InvalidTransaction
from utils import AccountAddressGenerator, SerializationHelper
from utils.enums import AccountType, AuthenticationStatus
from typing import Dict, Optional
from entities.accounts import (
    BuyerAccount, SellerAccount, ArtisanAccount, WorkshopAccount,
    DistributorAccount, WholesalerAccount, RetailerAccount,
    VerifierAccount, AdminAccount, SuperAdminAccount
)
import hashlib


class BaseSubHandler(ABC):
    """Abstract base class for subhandlers in the account transaction processor."""

    ACCOUNT_CLASSES = {
        AccountType.BUYER: BuyerAccount,
        AccountType.SELLER: SellerAccount,
        AccountType.ARTISAN: ArtisanAccount,
        AccountType.WORKSHOP: WorkshopAccount,
        AccountType.DISTRIBUTOR: DistributorAccount,
        AccountType.WHOLESALER: WholesalerAccount,
        AccountType.RETAILER: RetailerAccount,
        AccountType.VERIFIER: VerifierAccount,
        AccountType.ADMIN: AdminAccount,
        AccountType.SUPER_ADMIN: SuperAdminAccount
    }

    def __init__(self):
        self.address_generator = AccountAddressGenerator()
        self.serializer = SerializationHelper()
        

    def _validate_email_format(self, email: str):
        """Basic email format validation."""
        if not email or '@' not in email or '.' not in email.split('@')[-1]:
            raise InvalidTransaction("Invalid email format")
    
    def _check_email_not_registered(self, context: Context, email: str, exclude_public_key: str = None):
        """Check that email is not already registered."""
        existing_account = self._get_account_by_email(context, email)
        
        if existing_account and existing_account.get('public_key') != exclude_public_key:
            if not existing_account.get('is_deleted', False):
                raise InvalidTransaction(f"Email {email} is already registered")

    def _get_account_by_public_key(self, context: Context, public_key: str) -> Optional[Dict]:
        """Get account by public key."""
        try:
            account_address = self.address_generator.generate_account_address(public_key)
            entries = context.get_state([account_address])
            
            if entries:
                return self.serializer.from_bytes(entries[0].data)
            return None
        except:
            return None


    def _get_account_by_email(self, context: Context, email: str) -> Optional[Dict]:
        """Get account by email."""
        try:
            email_index_address = self.address_generator.generate_email_index_address(email)
            entries = context.get_state([email_index_address])
            
            if entries:
                email_data = self.serializer.from_bytes(entries[0].data)
                public_key = email_data.get('public_key')
                if public_key:
                    return self._get_account_by_public_key(context, public_key)
            return None
        except:
            return None

    def _check_public_key_not_registered(self, context: Context, public_key: str):
        """Check that public key is not already registered."""
        existing_account = self._get_account_by_public_key(context, public_key)
        
        if existing_account and not existing_account.get('is_deleted', False):
            raise InvalidTransaction(f"Public key is already registered")

    def _generate_account_id(self, email: str, account_type: AccountType, signer_public_key: str) -> str:
        """Generate deterministic account ID."""
        base_string = f"{email}_{account_type.value}_{signer_public_key}"
        return hashlib.sha256(base_string.encode()).hexdigest()[:16]
    
    def _store_account_with_indices(self, context: Context, account):
        """Store account and maintain all necessary indices."""
        # Convert account to dict for storage
        account_data = account.to_dict()
        
        # Store the account
        self._store_account(context, account_data)
        
        # Update email index
        self._update_email_index(context, account.email, account.account_id, account.public_key)
        
        # Update type index
        self._update_type_index(context, account.account_type.value, account.public_key)

    def _store_account(self, context: Context, account_data: Dict):
        """Store account data."""
        public_key = account_data['public_key']
        account_address = self.address_generator.generate_account_address(public_key)
        
        context.set_state({
            account_address: self.serializer.to_bytes(account_data)
        })

    def _update_email_index(self, context: Context, email: str, account_id: str, public_key: str):
        """Update email index."""
        email_address = self.address_generator.generate_email_index_address(email)
        email_data = {
            'email': email,
            'account_id': account_id,
            'public_key': public_key
        }
        context.set_state({
            email_address: self.serializer.to_bytes(email_data)
        })
    
    def _update_type_index(self, context: Context, account_type: str, public_key: str):
        """Update account type index."""
        type_address = self.address_generator.generate_type_index_address(account_type)
        
        try:
            entries = context.get_state([type_address])
            if entries:
                type_data = self.serializer.from_bytes(entries[0].data)
            else:
                type_data = {'account_type': account_type, 'public_keys': []}
            
            if public_key not in type_data['public_keys']:
                type_data['public_keys'].append(public_key)
            
            context.set_state({
                type_address: self.serializer.to_bytes(type_data)
            })
        except Exception as e:
            print(f"Warning: Could not update type index - {str(e)}")

    def _is_bootstrap_scenario(self, context: Context) -> bool:
        """Check if this is system bootstrap (no SuperAdmin exists)."""
        try:
            bootstrap_address = self.address_generator.generate_bootstrap_address()
            entries = context.get_state([bootstrap_address])
            return len(entries) == 0
        except:
            return True

    def _mark_bootstrap_complete(self, context: Context, admin_id: str, timestamp):
        """Mark system bootstrap as complete."""
        bootstrap_address = self.address_generator.generate_bootstrap_address()
        bootstrap_data = {
            'completed': True,
            'first_admin_id': admin_id,
            'timestamp': timestamp
        }
        context.set_state({
            bootstrap_address: self.serializer.to_bytes(bootstrap_data)
        })
    


    @abstractmethod
    def apply(self, transaction, context: Context, payload: dict):
        pass