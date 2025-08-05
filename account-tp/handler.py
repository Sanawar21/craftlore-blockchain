#!/usr/bin/env python3
"""
Account Transaction Handler for CraftLore Account TP.
Handles all account-related operations with complete privacy compliance.
"""

import json
import hashlib
from typing import Dict, List, Optional, Tuple
from sawtooth_sdk.processor.handler import TransactionHandler
from sawtooth_sdk.processor.context import Context
from sawtooth_sdk.processor.exceptions import InvalidTransaction

from entities.accounts import (
    BuyerAccount, SellerAccount, ArtisanAccount, WorkshopAccount,
    DistributorAccount, WholesalerAccount, RetailerAccount, 
    VerifierAccount, AdminAccount, SuperAdminAccount
)
from core.enums import AccountType, AuthenticationStatus
from core.exceptions import AccountError, AuthenticationError
from utils.address_generator import AccountAddressGenerator
from utils.serialization import SerializationHelper


class AccountTransactionHandler(TransactionHandler):
    """Transaction handler for CraftLore Account operations."""
    
    # Account type mapping
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
        self._family_name = 'craftlore-account'
        self._family_versions = ['1.0']
        
        self.address_generator = AccountAddressGenerator()
        self.serializer = SerializationHelper()
        self._namespaces = [self.address_generator.get_namespace()]
    
    @property
    def family_name(self):
        return self._family_name
    
    @property
    def family_versions(self):
        return self._family_versions
    
    @property
    def namespaces(self):
        return self._namespaces
    
    def apply(self, transaction, context: Context):
        """Apply account transaction."""
        print("Transaction received:", transaction.signature)
        try:
            # Parse payload
            payload = json.loads(transaction.payload.decode('utf-8'))
            action = payload.get('action')
            
            if not action:
                raise InvalidTransaction("Transaction must specify an action")
            
            # Route to specific action handler
            if action == 'account_create':
                return self._handle_create_account(transaction, context, payload)
            elif action == 'account_authenticate':
                return self._handle_authenticate_account(transaction, context, payload)
            elif action == 'account_update':
                return self._handle_update_account(transaction, context, payload)
            elif action == 'account_deactivate':
                return self._handle_deactivate_account(transaction, context, payload)
            elif action == 'account_query':
                return self._handle_query_account(transaction, context, payload)
            else:
                raise InvalidTransaction(f"Unknown account action: {action}")
                
        except json.JSONDecodeError:
            raise InvalidTransaction("Invalid JSON payload")
        except Exception as e:
            raise InvalidTransaction(f"Transaction processing error: {str(e)}")
    
    # =============================================
    # ACCOUNT CREATION
    # =============================================
    
    def _handle_create_account(self, transaction, context: Context, payload: Dict):
        """Handle account creation with privacy-first design."""
        # Validate required fields
        required_fields = ['account_type', 'email', 'timestamp']
        for field in required_fields:
            if field not in payload:
                raise InvalidTransaction(f"Missing required field: {field}")
        
        account_type_str = payload['account_type']
        email = payload['email']
        timestamp = payload.get('timestamp')
        
        # Validate inputs
        self._validate_email_format(email)
        
        try:
            account_type = AccountType(account_type_str)
        except ValueError:
            raise InvalidTransaction(f"Invalid account type: {account_type_str}")
        
        # Get signer information
        signer_public_key = transaction.header.signer_public_key
        
        # Check if email is already registered
        self._check_email_not_registered(context, email)
        
        # Check if public key is already registered
        self._check_public_key_not_registered(context, signer_public_key)
        
        # Generate account ID
        account_id = self._generate_account_id(email, account_type, signer_public_key)
        
        # Create account instance
        account_class = self.ACCOUNT_CLASSES.get(account_type)
        if not account_class:
            raise InvalidTransaction(f"Unsupported account type: {account_type_str}")
        
        account = account_class(
            account_id=account_id,
            public_key=signer_public_key,
            email=email,
            timestamp=timestamp
        )
        
        # Set initial authentication status
        if self._is_bootstrap_scenario(context) and account_type == AccountType.SUPER_ADMIN:
            account.authentication_status = AuthenticationStatus.APPROVED
        else:
            account.authentication_status = AuthenticationStatus.PENDING
        
        # Store account with all necessary indices
        self._store_account_with_indices(context, account)
        
        # Mark bootstrap complete for first SuperAdmin
        if account.authentication_status == AuthenticationStatus.APPROVED:
            self._mark_bootstrap_complete(context, account_id, timestamp)
        
        print(f"✅ Account created: {account_id} ({account_type_str})")
        
        return {
            'status': 'success',
            'account_id': account_id,
            'public_key': signer_public_key,
            'account_type': account_type_str,
            'authentication_status': account.authentication_status.value,
            'email': email
        }
    
    # =============================================
    # ACCOUNT AUTHENTICATION
    # =============================================
    
    def _handle_authenticate_account(self, transaction, context: Context, payload: Dict):
        """Handle account authentication (approval/rejection)."""
        required_fields = ['target_public_key', 'auth_decision', 'timestamp']
        for field in required_fields:
            if field not in payload:
                raise InvalidTransaction(f"Missing required field: {field}")
        
        target_public_key = payload['target_public_key']
        auth_decision = payload['auth_decision']
        timestamp = payload.get('timestamp')
        
        if auth_decision not in ['approve', 'reject']:
            raise InvalidTransaction("auth_decision must be 'approve' or 'reject'")
        
        # Get signer information and validate permissions
        signer_account = self._get_account_by_public_key(context, transaction.header.signer_public_key)
        if not signer_account:
            raise InvalidTransaction("Signer account not found")
        
        signer_type = AccountType(signer_account['account_type'])
        
        # Only admins and super admins can authenticate accounts
        if signer_type not in [AccountType.ADMIN, AccountType.SUPER_ADMIN]:
            raise InvalidTransaction("Only admins can authenticate accounts")
        
        # Load target account
        target_account = self._get_account_by_public_key(context, target_public_key)
        if not target_account:
            raise InvalidTransaction("Target account not found")
        
        target_type = AccountType(target_account['account_type'])
        
        # Validate permission hierarchy
        self._validate_authentication_permissions(signer_type, target_type)
        
        # Update authentication status
        new_status = AuthenticationStatus.APPROVED if auth_decision == 'approve' else AuthenticationStatus.REJECTED
        target_account['authentication_status'] = new_status.value
        
        # Add history entry
        self._add_account_history(target_account, {
            'action': f'authentication_{auth_decision}d',
            'actor_public_key': transaction.header.signer_public_key,
            'details': f'Account {auth_decision}d by {signer_type.value}',
            'timestamp': timestamp
        })
        
        # Store updated account
        self._store_account(context, target_account)
        
        print(f"✅ Account {auth_decision}d: {target_account['account_id']}")
        
        return {
            'status': 'success',
            'account_id': target_account['account_id'],
            'public_key': target_public_key,
            'new_auth_status': new_status.value
        }
    
    # =============================================
    # ACCOUNT UPDATE
    # =============================================
    
    def _handle_update_account(self, transaction, context: Context, payload: Dict):
        """Handle account updates."""

        required_fields = ['target_public_key', 'timestamp']
        for field in required_fields:
            if field not in payload:
                raise InvalidTransaction(f"Missing required field: {field}")

        signer_public_key = transaction.header.signer_public_key
        target_public_key = payload.get('target_public_key', signer_public_key)
        timestamp = payload.get('timestamp')
        
        # Load accounts
        signer_account = self._get_account_by_public_key(context, signer_public_key)
        target_account = self._get_account_by_public_key(context, target_public_key)
        
        if not signer_account or not target_account:
            raise InvalidTransaction("Account not found")
        
        signer_type = AccountType(signer_account['account_type'])
        target_type = AccountType(target_account['account_type'])
        
        # Validate update permissions
        self._validate_update_permissions(signer_public_key, signer_type, target_public_key, target_type)
        
        # Apply updates
        updated_fields = []
        
        # Update email if provided
        if 'email' in payload:
            new_email = payload['email']
            self._validate_email_format(new_email)
            self._check_email_not_registered(context, new_email, exclude_public_key=target_public_key)
            
            old_email = target_account.get('email')
            target_account['email'] = new_email
            updated_fields.append(f'email: {old_email} -> {new_email}')
            
            # Update email index
            self._update_email_index(context, new_email, target_account['account_id'], target_public_key)
        
        # Update other account-type-specific fields
        updatable_fields = self._get_updatable_fields(target_type)
        for field in updatable_fields:
            if field in payload and field != 'email':
                old_value = target_account.get(field, '')
                target_account[field] = payload[field]
                updated_fields.append(f'{field}: {old_value} -> {payload[field]}')
        
        # Add history entry if fields were updated
        if updated_fields:
            self._add_account_history(target_account, {
                'action': 'account_updated',
                'actor_public_key': signer_public_key,
                'details': f'Updated fields: {", ".join(updated_fields)}',
                'timestamp': timestamp
            })
            
            # Store updated account
            self._store_account(context, target_account)
            
            print(f"✅ Account updated: {target_account['account_id']}")
        
        return {
            'status': 'success',
            'account_id': target_account['account_id'],
            'updated_fields': updated_fields
        }
    
    # =============================================
    # ACCOUNT DEACTIVATION
    # =============================================
    
    def _handle_deactivate_account(self, transaction, context: Context, payload: Dict):
        """Handle account deactivation."""
        required_fields = ['target_public_key', 'timestamp']
        for field in required_fields:
            if field not in payload:
                raise InvalidTransaction(f"Missing required field: {field}")
        
        target_public_key = payload['target_public_key']
        timestamp = payload['timestamp']
        signer_public_key = transaction.header.signer_public_key
        
        # Load accounts
        signer_account = self._get_account_by_public_key(context, signer_public_key)
        target_account = self._get_account_by_public_key(context, target_public_key)
        
        if not signer_account or not target_account:
            raise InvalidTransaction("Account not found")
        
        signer_type = AccountType(signer_account['account_type'])
        target_type = AccountType(target_account['account_type'])
        
        # Validate deactivation permissions
        self._validate_deactivation_permissions(signer_public_key, signer_type, target_public_key, target_type)
        
        # Mark account as deleted
        target_account['is_deleted'] = True
        target_account['authentication_status'] = AuthenticationStatus.REJECTED.value
        
        # Add history entry
        self._add_account_history(target_account, {
            'action': 'account_deactivated',
            'actor_public_key': signer_public_key,
            'details': f'Account deactivated by {signer_type.value}',
            'timestamp': timestamp
        })
        
        # Store updated account
        self._store_account(context, target_account)
        
        print(f"✅ Account deactivated: {target_account['account_id']}")
        
        return {
            'status': 'success',
            'account_id': target_account['account_id'],
            'deactivated': True
        }
    
    # =============================================
    # ACCOUNT QUERY
    # =============================================
    
    def _handle_query_account(self, transaction, context: Context, payload: Dict):
        """Handle account queries."""
        query_type = payload.get('query_type', 'by_public_key')
        
        if query_type == 'by_public_key':
            public_key = payload.get('public_key', transaction.header.signer_public_key)
            account = self._get_account_by_public_key(context, public_key)
            
        elif query_type == 'by_email':
            email = payload.get('email')
            if not email:
                raise InvalidTransaction("Email required for email query")
            account = self._get_account_by_email(context, email)
            
        elif query_type == 'by_account_type':
            account_type = payload.get('account_type')
            if not account_type:
                raise InvalidTransaction("Account type required for type query")
            accounts = self._get_accounts_by_type(context, account_type)
            return {
                'status': 'success',
                'query_type': query_type,
                'account_type': account_type,
                'accounts': accounts
            }
        else:
            raise InvalidTransaction(f"Unknown query type: {query_type}")
        
        if not account:
            return {
                'status': 'not_found',
                'query_type': query_type
            }
        
        # Remove sensitive data for response
        safe_account = self._prepare_safe_account_response(account)
        
        return {
            'status': 'success',
            'query_type': query_type,
            'account': safe_account
        }
    
    # =============================================
    # HELPER METHODS
    # =============================================
    
    def _generate_account_id(self, email: str, account_type: AccountType, signer_public_key: str) -> str:
        """Generate deterministic account ID."""
        base_string = f"{email}_{account_type.value}_{signer_public_key}"
        return hashlib.sha256(base_string.encode()).hexdigest()[:16]
    
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
    
    def _check_public_key_not_registered(self, context: Context, public_key: str):
        """Check that public key is not already registered."""
        existing_account = self._get_account_by_public_key(context, public_key)
        
        if existing_account and not existing_account.get('is_deleted', False):
            raise InvalidTransaction(f"Public key is already registered")
    
    def _is_bootstrap_scenario(self, context: Context) -> bool:
        """Check if this is system bootstrap (no SuperAdmin exists)."""
        try:
            bootstrap_address = self.address_generator.generate_bootstrap_address()
            entries = context.get_state([bootstrap_address])
            return len(entries) == 0
        except:
            return True
    
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
    
    def _get_accounts_by_type(self, context: Context, account_type: str) -> List[Dict]:
        """Get all accounts of a specific type."""
        try:
            type_index_address = self.address_generator.generate_type_index_address(account_type)
            entries = context.get_state([type_index_address])
            
            if entries:
                type_data = self.serializer.from_bytes(entries[0].data)
                public_keys = type_data.get('public_keys', [])
                
                accounts = []
                for public_key in public_keys:
                    account = self._get_account_by_public_key(context, public_key)
                    if account and not account.get('is_deleted', False):
                        accounts.append(self._prepare_safe_account_response(account))
                
                return accounts
            return []
        except:
            return []
    
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
    
    def _add_account_history(self, account_data: Dict, history_entry: Dict, timestamp):
        """Add history entry to account."""
        if 'history' not in account_data:
            account_data['history'] = []
        
        history_entry['timestamp'] = timestamp
        account_data['history'].append(history_entry)
    
    def _validate_authentication_permissions(self, signer_type: AccountType, target_type: AccountType):
        """Validate authentication permissions."""
        if signer_type == AccountType.SUPER_ADMIN:
            return  # Super admin can authenticate anyone
        elif signer_type == AccountType.ADMIN:
            allowed_types = [
                AccountType.BUYER, AccountType.SELLER, AccountType.ARTISAN,
                AccountType.WORKSHOP, AccountType.DISTRIBUTOR, AccountType.WHOLESALER,
                AccountType.RETAILER, AccountType.VERIFIER
            ]
            if target_type not in allowed_types:
                raise InvalidTransaction("Admins cannot authenticate other admins or super admins")
        else:
            raise InvalidTransaction("Only admins can authenticate accounts")
    
    def _validate_update_permissions(self, signer_key: str, signer_type: AccountType, target_key: str, target_type: AccountType):
        """Validate update permissions."""
        # Users can update their own accounts
        if signer_key == target_key:
            return
        
        # Super admins can update anyone except other super admins
        if signer_type == AccountType.SUPER_ADMIN:
            if target_type == AccountType.SUPER_ADMIN:
                raise InvalidTransaction("Super admins cannot update other super admins")
            return
        
        # Admins can update certain account types
        if signer_type == AccountType.ADMIN:
            allowed_types = [
                AccountType.BUYER, AccountType.SELLER, AccountType.ARTISAN,
                AccountType.WORKSHOP, AccountType.DISTRIBUTOR, AccountType.WHOLESALER,
                AccountType.RETAILER, AccountType.VERIFIER
            ]
            if target_type not in allowed_types:
                raise InvalidTransaction("Admins cannot update other admins or super admins")
            return
        
        raise InvalidTransaction("Insufficient permissions to update account")
    
    def _validate_deactivation_permissions(self, signer_key: str, signer_type: AccountType, target_key: str, target_type: AccountType):
        """Validate deactivation permissions."""
        # Cannot deactivate self
        if signer_key == target_key:
            raise InvalidTransaction("Cannot deactivate your own account")
        
        # Super admins can deactivate anyone except other super admins
        if signer_type == AccountType.SUPER_ADMIN:
            if target_type == AccountType.SUPER_ADMIN:
                raise InvalidTransaction("Super admins cannot deactivate other super admins")
            return
        
        # Admins can deactivate certain account types
        if signer_type == AccountType.ADMIN:
            allowed_types = [
                AccountType.BUYER, AccountType.SELLER, AccountType.ARTISAN,
                AccountType.WORKSHOP, AccountType.DISTRIBUTOR, AccountType.WHOLESALER,
                AccountType.RETAILER, AccountType.VERIFIER
            ]
            if target_type not in allowed_types:
                raise InvalidTransaction("Admins cannot deactivate other admins or super admins")
            return
        
        raise InvalidTransaction("Insufficient permissions to deactivate account")
    
    def _get_updatable_fields(self, account_type: AccountType) -> List[str]:
        """Get list of fields that can be updated for each account type."""
        base_fields = []  # Only email by default
        
        if account_type == AccountType.SELLER:
            return base_fields + ['business_name', 'business_type', 'registration_number']
        elif account_type == AccountType.ARTISAN:
            return base_fields + ['specialization', 'skill_level', 'years_experience']
        elif account_type == AccountType.WORKSHOP:
            return base_fields + ['workshop_type', 'capacity_artisans', 'certifications']
        elif account_type == AccountType.VERIFIER:
            return base_fields + ['specialization', 'certification_level', 'credentials']
        else:
            return base_fields
    
    def _prepare_safe_account_response(self, account: Dict) -> Dict:
        """Prepare account data for safe response (remove sensitive fields)."""
        safe_account = account.copy()
        
        # Always include these safe fields
        safe_fields = [
            'account_id', 'public_key', 'email', 'account_type',
            'authentication_status', 'verification_status', 'created_timestamp',
            'specialization', 'skill_level', 'region', 'certifications'
        ]
        
        # Create response with only safe fields
        response = {}
        for field in safe_fields:
            if field in safe_account:
                response[field] = safe_account[field]
        
        return response
