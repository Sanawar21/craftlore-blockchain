#!/usr/bin/env python3
"""
Transaction handlers for the CraftLore blockchain system.
These handlers process different types of transactions for the Kashmiri handicrafts sector.
"""

import json
import hashlib
from typing import Dict, List, Any
from sawtooth_sdk.processor.handler import TransactionHandler
from sawtooth_sdk.processor.context import Context
from sawtooth_sdk.processor.exceptions import InvalidTransaction

# Import our object classes
from object import CraftloreObject, AuthenticationStatus, AccountType
from accounts import (
    Account, SuperAdminAccount, ArtisanAdminAccount, ArtisanAccount,
    SupplierAccount, WorkshopAccount, DistributorAccount,
    WholesalerAccount, RetailerAccount, BuyerAccount
)

class CraftLoreTransactionHandler(TransactionHandler):
    """Base transaction handler for CraftLore objects."""
    
    @property
    def family_name(self):
        return 'craftlore'
    
    @property
    def family_versions(self):
        return ['1.0']
    
    @property
    def namespaces(self):
        # CraftLore namespace (first 6 characters of SHA-512 hash of 'craftlore')
        return [hashlib.sha512('craftlore'.encode('utf-8')).hexdigest()[:6]]
    
    def apply(self, transaction, context: Context):
        """Main entry point for transaction processing."""
        try:
            # Parse transaction payload
            payload = json.loads(transaction.payload.decode('utf-8'))
            action = payload.get('action')
            
            # Route to appropriate handler
            if action.startswith('account_'):
                return self._handle_account_transaction(transaction, context, payload)
            elif action.startswith('material_'):
                return self._handle_material_transaction(transaction, context, payload)
            elif action.startswith('product_'):
                return self._handle_product_transaction(transaction, context, payload)
            elif action.startswith('workshop_'):
                return self._handle_workshop_transaction(transaction, context, payload)
            elif action.startswith('order_'):
                return self._handle_order_transaction(transaction, context, payload)
            elif action.startswith('shipment_'):
                return self._handle_shipment_transaction(transaction, context, payload)
            elif action.startswith('transaction_'):
                return self._handle_business_transaction(transaction, context, payload)
            elif action.startswith('certificate_'):
                return self._handle_certificate_transaction(transaction, context, payload)
            elif action.startswith('review_'):
                return self._handle_review_transaction(transaction, context, payload)
            else:
                raise InvalidTransaction(f"Unknown action: {action}")
                
        except json.JSONDecodeError:
            raise InvalidTransaction("Invalid JSON payload")
        except Exception as e:
            raise InvalidTransaction(f"Transaction processing error: {str(e)}")
    
    def _get_signer_info(self, transaction, context: Context, action: str = None) -> tuple:
        """Extract signer information from transaction and validate against blockchain state."""
        signer_public_key = transaction.header.signer_public_key
        
        # Look up account by public key
        account_info = self._get_account_by_public_key(context, signer_public_key)
        
        if account_info:
            account_id = account_info.get('account_id')
            account_type = AccountType(account_info.get('account_type'))
            auth_status = AuthenticationStatus(account_info.get('auth_status', 'PENDING'))
            
            # Validate access based on action and account status
            self._validate_access(action, auth_status, account_type, signer_public_key)
            
            return account_id, account_type, auth_status
        else:
            # Handle bootstrap case and unauthorized access
            return self._handle_unregistered_signer(context, signer_public_key, action)
    
    def _generate_address(self, prefix: str, identifier: str) -> str:
        """Generate blockchain address for storage."""
        return hashlib.sha512(
            f"craftlore_{prefix}_{identifier}".encode('utf-8')
        ).hexdigest()[:70]
    
    def _get_account_by_public_key(self, context: Context, public_key: str) -> Dict:
        """Look up account information by public key."""
        try:
            # Check public key index
            pubkey_address = self._generate_address('pubkey_index', public_key)
            entries = context.get_state([pubkey_address])
            
            if entries:
                pubkey_data = json.loads(entries[0].data.decode('utf-8'))
                account_id = pubkey_data.get('account_id')
                
                if account_id:
                    # Load the full account to get current status
                    account_data = self._load_object(context, 'account', account_id)
                    if account_data and not account_data.get('is_deleted', False):
                        return {
                            'account_id': account_id,
                            'account_type': account_data.get('account_type'),
                            'auth_status': account_data.get('authentication_status', 'PENDING'),
                            'public_key': public_key
                        }
            return None
        except InvalidTransaction:
            return None
    
    def _validate_access(self, action: str, auth_status: AuthenticationStatus, 
                        account_type: AccountType, public_key: str):
        """Validate if the signer has access to perform the requested action."""
        
        # Define access control matrix
        if auth_status == AuthenticationStatus.REJECTED:
            raise InvalidTransaction(f"Access denied: Account with public key {public_key[:16]}... has been rejected")
        
        # Actions allowed for PENDING accounts
        pending_allowed_actions = ['account_authenticate', 'account_update']
        
        if auth_status == AuthenticationStatus.PENDING:
            if action and not any(action.startswith(allowed) for allowed in pending_allowed_actions):
                raise InvalidTransaction(f"Access denied: Account authentication is pending. Only account authentication/update operations are allowed.")
        
        # For APPROVED accounts, all actions are allowed
        # Additional role-based checks can be added here
        
    def _handle_unregistered_signer(self, context: Context, public_key: str, action: str) -> tuple:
        """Handle cases where the signer doesn't have a registered account."""
        
        # Check if this is a bootstrap scenario (no accounts exist yet)
        if self._is_bootstrap_scenario(context):
            if action == 'account_create':
                # Allow creation of first SuperAdmin account
                return public_key, AccountType.SUPER_ADMIN, AuthenticationStatus.APPROVED
            else:
                raise InvalidTransaction("System bootstrap required: Create the first SuperAdmin account")
        
        # For non-bootstrap scenarios, only allow account creation
        if action == 'account_create':
            # Return minimal permissions for account creation
            return public_key, AccountType.BUYER, AuthenticationStatus.PENDING  # Lowest privilege
        else:
            raise InvalidTransaction(f"Access denied: No account registered for public key {public_key[:16]}...")
    
    def _is_bootstrap_scenario(self, context: Context) -> bool:
        """Check if this is a bootstrap scenario (no accounts exist yet)."""
        try:
            # Try to find any existing SuperAdmin account
            # In a real implementation, you might maintain a system state counter
            # For now, we'll use a simple heuristic
            
            # Check if there's a bootstrap marker or any accounts at all
            bootstrap_address = self._generate_address('system', 'bootstrap_complete')
            entries = context.get_state([bootstrap_address])
            return len(entries) == 0  # Bootstrap not completed
            
        except Exception:
            return True  # Assume bootstrap needed if we can't determine
    
    def _store_object(self, context: Context, obj: CraftloreObject):
        """Store object in blockchain state."""
        object_address = obj.get_object_address()
        history_address = obj.get_history_address()
        
        # Store main object
        context.set_state({
            object_address: json.dumps(obj.to_dict()).encode('utf-8')
        })
        
        # Store history separately
        history_data = {
            'object_id': obj.identifier,
            'object_type': obj.type,
            'history': [entry.to_dict() for entry in obj.history]
        }
        context.set_state({
            history_address: json.dumps(history_data).encode('utf-8')
        })
    
    def _load_object(self, context: Context, object_type: str, object_id: str) -> Dict:
        """Load object from blockchain state."""
        address = self._generate_address(object_type, object_id)
        entries = context.get_state([address])
        
        if not entries:
            raise InvalidTransaction(f"{object_type} {object_id} not found")
        
        return json.loads(entries[0].data.decode('utf-8'))
    
    def _check_account_exists(self, context: Context, identifier: str = None, email: str = None) -> bool:
        """Check if an account already exists by ID or email."""
        if identifier:
            try:
                existing = self._load_object(context, 'account', identifier)
                if existing and not existing.get('is_deleted', False):
                    return True
            except InvalidTransaction:
                pass  # Account not found, which is fine
        
        if email:
            # Check email index
            email_address = self._generate_address('email_index', email)
            entries = context.get_state([email_address])
            if entries:
                email_data = json.loads(entries[0].data.decode('utf-8'))
                account_id = email_data.get('account_id')
                if account_id:
                    try:
                        existing = self._load_object(context, 'account', account_id)
                        if existing and not existing.get('is_deleted', False):
                            return True
                    except InvalidTransaction:
                        pass
        
        return False
    
    def _check_object_exists(self, context: Context, object_type: str, identifier: str) -> bool:
        """Check if any object already exists by type and identifier."""
        try:
            existing = self._load_object(context, object_type, identifier)
            if existing and not existing.get('is_deleted', False):
                return True
        except InvalidTransaction:
            pass  # Object not found, which is fine
        return False
    
    def _store_account_with_indices(self, context: Context, account, public_key: str = None):
        """Store account and maintain email and public key indices."""
        # Store the main account object
        self._store_object(context, account)
        
        # Maintain email index if email exists
        if hasattr(account, 'email') and account.email:
            email_address = self._generate_address('email_index', account.email)
            email_index_data = {
                'email': account.email,
                'account_id': account.identifier,
                'account_type': account.account_type.value if hasattr(account, 'account_type') else 'unknown'
            }
            context.set_state({
                email_address: json.dumps(email_index_data).encode('utf-8')
            })
        
        # Maintain public key index if public key provided
        if public_key:
            pubkey_address = self._generate_address('pubkey_index', public_key)
            pubkey_index_data = {
                'public_key': public_key,
                'account_id': account.identifier,
                'account_type': account.account_type.value if hasattr(account, 'account_type') else 'unknown',
                'auth_status': account.authentication_status.value if hasattr(account, 'authentication_status') else 'PENDING'
            }
            context.set_state({
                pubkey_address: json.dumps(pubkey_index_data).encode('utf-8')
            })
        
        # Mark bootstrap as complete if this is a SuperAdmin account
        if hasattr(account, 'account_type') and account.account_type == AccountType.SUPER_ADMIN:
            bootstrap_address = self._generate_address('system', 'bootstrap_complete')
            bootstrap_data = {
                'completed': True,
                'first_admin_id': account.identifier,
                'timestamp': account.created_timestamp if hasattr(account, 'created_timestamp') else ''
            }
            context.set_state({
                bootstrap_address: json.dumps(bootstrap_data).encode('utf-8')
            })

    # =============================================
    # ACCOUNT TRANSACTION HANDLERS
    # =============================================
    
    def _handle_account_transaction(self, transaction, context: Context, payload: Dict):
        """Handle account-related transactions."""
        action = payload.get('action')
        signer_id, signer_type, auth_status = self._get_signer_info(transaction, context, action)
        
        if action == 'account_create':
            return self._create_account(transaction, context, payload, signer_id, signer_type)
        elif action == 'account_authenticate':
            return self._authenticate_account(transaction, context, payload, signer_id, signer_type)
        elif action == 'account_update':
            return self._update_account(transaction, context, payload, signer_id, signer_type)
        elif action == 'account_delete':
            return self._delete_account(transaction, context, payload, signer_id, signer_type)
        else:
            raise InvalidTransaction(f"Unknown account action: {action}")
    
    def _create_account(self, transaction, context: Context, payload: Dict, signer_id: str, signer_type: AccountType):
        """Create a new account."""
        account_type = AccountType(payload.get('account_type'))
        account_data = payload.get('account_data', {})
        signer_public_key = transaction.header.signer_public_key
        
        # Extract identifier and email for duplicate checking
        proposed_id = account_data.get('account_id') or account_data.get('identifier')
        email = account_data.get('email')
        
        # Check for duplicate accounts
        if self._check_account_exists(context, identifier=proposed_id, email=email):
            if proposed_id:
                raise InvalidTransaction(f"Account with ID '{proposed_id}' already exists")
            elif email:
                raise InvalidTransaction(f"Account with email '{email}' already exists")
            else:
                raise InvalidTransaction("Account already exists")
        
        # Check if public key is already registered
        existing_account = self._get_account_by_public_key(context, signer_public_key)
        if existing_account:
            raise InvalidTransaction(f"Public key {signer_public_key[:16]}... is already registered to account {existing_account['account_id']}")
        
        # Choose appropriate account class
        account_classes = {
            AccountType.SUPER_ADMIN: SuperAdminAccount,
            AccountType.ARTISAN_ADMIN: ArtisanAdminAccount,
            AccountType.ARTISAN: ArtisanAccount,
            AccountType.SUPPLIER: SupplierAccount,
            AccountType.WORKSHOP: WorkshopAccount,
            AccountType.DISTRIBUTOR: DistributorAccount,
            AccountType.WHOLESALER: WholesalerAccount,
            AccountType.RETAILER: RetailerAccount,
            AccountType.BUYER: BuyerAccount,
        }
        
        AccountClass = account_classes.get(account_type, Account)
        
        # Create account object
        account = AccountClass.new(
            creator_id=signer_id,
            **account_data
        )
        
        # Store account with indices (including public key mapping)
        self._store_account_with_indices(context, account, signer_public_key)
        
        print(f"✅ Account created: {account.identifier} ({account.account_type.value}) for public key {signer_public_key[:16]}...")
    
    def _authenticate_account(self, transaction, context: Context, payload: Dict, signer_id: str, signer_type: AccountType):
        """Authenticate an account."""
        account_id = payload.get('account_id')
        status = AuthenticationStatus(payload.get('status'))
        reason = payload.get('reason', '')
        
        # Load account
        account_data = self._load_object(context, 'account', account_id)
        account = Account.from_dict(account_data)
        
        # Authenticate
        account.authenticate(
            approver_id=signer_id,
            account_type=signer_type,
            status=status,
            reason=reason,
            block_number=payload.get('block_number', 0),
            transaction_id=transaction.header_signature
        )
        
        # Store updated account
        self._store_object(context, account)
        
        # Update public key index with new authentication status
        self._update_public_key_index_status(context, account_id, status)
        
        print(f"✅ Account authenticated: {account_id} -> {status.value}")
    
    def _update_public_key_index_status(self, context: Context, account_id: str, new_status: AuthenticationStatus):
        """Update the authentication status in the public key index."""
        try:
            # We need to find the public key for this account
            # This is a bit inefficient, but necessary for maintaining consistency
            # In a production system, you might store the public key in the account object
            
            # For now, we'll scan through possible public key indices
            # This is not optimal but works for the demo
            # In production, store public_key in the account object itself
            
            account_data = self._load_object(context, 'account', account_id)
            if hasattr(account_data, 'public_key') or 'public_key' in account_data:
                public_key = account_data.get('public_key') or getattr(account_data, 'public_key', None)
                if public_key:
                    pubkey_address = self._generate_address('pubkey_index', public_key)
                    
                    # Update the index
                    pubkey_index_data = {
                        'public_key': public_key,
                        'account_id': account_id,
                        'account_type': account_data.get('account_type'),
                        'auth_status': new_status.value
                    }
                    context.set_state({
                        pubkey_address: json.dumps(pubkey_index_data).encode('utf-8')
                    })
        except Exception as e:
            # Log the error but don't fail the transaction
            print(f"⚠️  Warning: Could not update public key index: {str(e)}")

    # =============================================
    # MATERIAL TRANSACTION HANDLERS
    # =============================================
    
    def _handle_material_transaction(self, transaction, context: Context, payload: Dict):
        """Handle raw material transactions."""
        action = payload.get('action')
        signer_id, signer_type, auth_status = self._get_signer_info(transaction, context, action)
        
        if action == 'material_harvest':
            return self._record_material_harvest(transaction, context, payload, signer_id, signer_type)
        elif action == 'material_certify':
            return self._certify_material(transaction, context, payload, signer_id, signer_type)
        elif action == 'material_transfer':
            return self._transfer_material(transaction, context, payload, signer_id, signer_type)
        else:
            raise InvalidTransaction(f"Unknown material action: {action}")
    
    def _record_material_harvest(self, transaction, context: Context, payload: Dict, signer_id: str, signer_type: AccountType):
        """Record raw material harvesting."""
        material_data = payload.get('material_data', {})
        
        # Check for duplicate material ID if provided
        proposed_id = material_data.get('material_id')
        if proposed_id and self._check_object_exists(context, 'raw_material', proposed_id):
            raise InvalidTransaction(f"Material with ID '{proposed_id}' already exists")
        
        # Create material object
        material = RawMaterial.new(
            supplier_id=signer_id,
            creator_id=signer_id,
            **material_data
        )
        
        # Store in blockchain
        self._store_object(context, material)
        
        print(f"✅ Material harvested: {material.identifier}")

    # =============================================
    # PRODUCT TRANSACTION HANDLERS
    # =============================================
    
    def _handle_product_transaction(self, transaction, context: Context, payload: Dict):
        """Handle product-related transactions."""
        action = payload.get('action')
        signer_id, signer_type, auth_status = self._get_signer_info(transaction, context, action)
        
        if action == 'product_create':
            return self._create_product(transaction, context, payload, signer_id, signer_type)
        elif action == 'product_update_progress':
            return self._update_product_progress(transaction, context, payload, signer_id, signer_type)
        elif action == 'product_complete':
            return self._complete_product(transaction, context, payload, signer_id, signer_type)
        elif action == 'product_quality_check':
            return self._quality_check_product(transaction, context, payload, signer_id, signer_type)
        else:
            raise InvalidTransaction(f"Unknown product action: {action}")
    
    def _create_product(self, transaction, context: Context, payload: Dict, signer_id: str, signer_type: AccountType):
        """Create a new product."""
        product_data = payload.get('product_data', {})
        
        # Check for duplicate product ID if provided
        proposed_id = product_data.get('product_id')
        if proposed_id and self._check_object_exists(context, 'handicraft_product', proposed_id):
            raise InvalidTransaction(f"Product with ID '{proposed_id}' already exists")
        
        # Create product object
        product = HandicraftProduct.new(
            artisan_id=signer_id,
            creator_id=signer_id,
            **product_data
        )
        
        # Store in blockchain
        self._store_object(context, product)
        
        print(f"✅ Product created: {product.identifier}")

    # =============================================
    # WORKSHOP TRANSACTION HANDLERS
    # =============================================
    
    def _handle_workshop_transaction(self, transaction, context: Context, payload: Dict):
        """Handle workshop-related transactions."""
        action = payload.get('action')
        signer_id, signer_type, auth_status = self._get_signer_info(transaction, context, action)
        
        if action == 'workshop_register':
            return self._register_workshop(transaction, context, payload, signer_id, signer_type)
        elif action == 'workshop_intake_material':
            return self._workshop_material_intake(transaction, context, payload, signer_id, signer_type)
        elif action == 'workshop_assign_artisan':
            return self._assign_artisan_to_workshop(transaction, context, payload, signer_id, signer_type)
        else:
            raise InvalidTransaction(f"Unknown workshop action: {action}")

    # =============================================
    # ORDER TRANSACTION HANDLERS
    # =============================================
    
    def _handle_order_transaction(self, transaction, context: Context, payload: Dict):
        """Handle order-related transactions."""
        action = payload.get('action')
        signer_id, signer_type, auth_status = self._get_signer_info(transaction, context, action)
        
        if action == 'order_create':
            return self._create_work_order(transaction, context, payload, signer_id, signer_type)
        elif action == 'order_assign':
            return self._assign_work_order(transaction, context, payload, signer_id, signer_type)
        elif action == 'order_complete':
            return self._complete_work_order(transaction, context, payload, signer_id, signer_type)
        else:
            raise InvalidTransaction(f"Unknown order action: {action}")

    # =============================================
    # SHIPMENT TRANSACTION HANDLERS
    # =============================================
    
    def _handle_shipment_transaction(self, transaction, context: Context, payload: Dict):
        """Handle shipment and logistics transactions."""
        action = payload.get('action')
        signer_id, signer_type, auth_status = self._get_signer_info(transaction, context, action)
        
        if action == 'shipment_create':
            return self._create_shipment(transaction, context, payload, signer_id, signer_type)
        elif action == 'shipment_update_location':
            return self._update_shipment_location(transaction, context, payload, signer_id, signer_type)
        elif action == 'shipment_deliver':
            return self._deliver_shipment(transaction, context, payload, signer_id, signer_type)
        else:
            raise InvalidTransaction(f"Unknown shipment action: {action}")

    # =============================================
    # BUSINESS TRANSACTION HANDLERS
    # =============================================
    
    def _handle_business_transaction(self, transaction, context: Context, payload: Dict):
        """Handle business transactions (purchases, sales, etc.)."""
        action = payload.get('action')
        signer_id, signer_type, auth_status = self._get_signer_info(transaction, context, action)
        
        if action == 'transaction_purchase':
            return self._record_purchase(transaction, context, payload, signer_id, signer_type)
        elif action == 'transaction_payment':
            return self._record_payment(transaction, context, payload, signer_id, signer_type)
        elif action == 'transaction_royalty':
            return self._distribute_royalty(transaction, context, payload, signer_id, signer_type)
        else:
            raise InvalidTransaction(f"Unknown transaction action: {action}")

    # =============================================
    # CERTIFICATE TRANSACTION HANDLERS
    # =============================================
    
    def _handle_certificate_transaction(self, transaction, context: Context, payload: Dict):
        """Handle certificate and verification transactions."""
        action = payload.get('action')
        signer_id, signer_type, auth_status = self._get_signer_info(transaction, context, action)
        
        if action == 'certificate_issue':
            return self._issue_certificate(transaction, context, payload, signer_id, signer_type)
        elif action == 'certificate_verify':
            return self._verify_certificate(transaction, context, payload, signer_id, signer_type)
        elif action == 'certificate_revoke':
            return self._revoke_certificate(transaction, context, payload, signer_id, signer_type)
        else:
            raise InvalidTransaction(f"Unknown certificate action: {action}")

    # =============================================
    # REVIEW TRANSACTION HANDLERS
    # =============================================
    
    def _handle_review_transaction(self, transaction, context: Context, payload: Dict):
        """Handle review and rating transactions."""
        action = payload.get('action')
        signer_id, signer_type, auth_status = self._get_signer_info(transaction, context, action)
        
        if action == 'review_create':
            return self._create_review(transaction, context, payload, signer_id, signer_type)
        elif action == 'review_update':
            return self._update_review(transaction, context, payload, signer_id, signer_type)
        else:
            raise InvalidTransaction(f"Unknown review action: {action}")


# =============================================
# SPECIFIC OBJECT CLASSES FOR BLOCKCHAIN
# =============================================

class RawMaterial(CraftloreObject):
    """Raw material object for blockchain storage."""
    
    def __init__(self, **kwargs):
        # Material-specific attributes
        self.material_id = kwargs.get('material_id', self.generate_unique_identifier())
        self.supplier_id = kwargs.get('supplier_id', '')
        self.material_type = kwargs.get('material_type', '')  # wool, silk, wood, etc.
        self.harvest_date = kwargs.get('harvest_date', '')
        self.quantity = kwargs.get('quantity', 0)
        self.source_location = kwargs.get('source_location', '')  # geo-tagged
        self.certifications = kwargs.get('certifications', [])  # organic, sustainable, etc.
        
        # Remove from kwargs to avoid conflicts
        kwargs_copy = kwargs.copy()
        material_attrs = ['material_id', 'supplier_id', 'material_type', 'harvest_date', 'quantity', 'source_location', 'certifications']
        for key in material_attrs:
            kwargs_copy.pop(key, None)
        
        super().__init__(**kwargs_copy)
    
    @property
    def identifier(self):
        return self.material_id
    
    @property
    def creator(self):
        return self.supplier_id
    
    @property
    def type(self):
        return 'raw_material'
    
    @property
    def owner(self):
        return getattr(self, 'owner_id', self.supplier_id)


class HandicraftProduct(CraftloreObject):
    """Handicraft product object for blockchain storage."""
    
    def __init__(self, **kwargs):
        # Product-specific attributes
        self.product_id = kwargs.get('product_id', self.generate_unique_identifier())
        self.artisan_id = kwargs.get('artisan_id', '')
        self.workshop_id = kwargs.get('workshop_id', '')
        self.product_name = kwargs.get('product_name', '')
        self.product_type = kwargs.get('product_type', '')  # carpet, shawl, woodwork, etc.
        self.materials_used = kwargs.get('materials_used', [])  # List of material IDs
        self.production_stages = kwargs.get('production_stages', [])
        self.estimated_completion = kwargs.get('estimated_completion', '')
        self.actual_completion = kwargs.get('actual_completion', '')
        self.quality_reports = kwargs.get('quality_reports', [])
        self.gi_certification = kwargs.get('gi_certification', '')
        self.nft_id = kwargs.get('nft_id', '')
        self.price = kwargs.get('price', 0.0)
        
        # Remove from kwargs to avoid conflicts
        kwargs_copy = kwargs.copy()
        product_attrs = ['product_id', 'artisan_id', 'workshop_id', 'product_name', 'product_type', 
                        'materials_used', 'production_stages', 'estimated_completion', 'actual_completion',
                        'quality_reports', 'gi_certification', 'nft_id', 'price']
        for key in product_attrs:
            kwargs_copy.pop(key, None)
        
        super().__init__(**kwargs_copy)
    
    @property
    def identifier(self):
        return self.product_id
    
    @property
    def creator(self):
        return self.artisan_id
    
    @property
    def type(self):
        return 'handicraft_product'
    
    @property
    def owner(self):
        return getattr(self, 'owner_id', self.artisan_id)


class WorkOrder(CraftloreObject):
    """Work order object for blockchain storage."""
    
    def __init__(self, **kwargs):
        # Order-specific attributes
        self.order_id = kwargs.get('order_id', self.generate_unique_identifier())
        self.artisan_id = kwargs.get('artisan_id', '')
        self.workshop_id = kwargs.get('workshop_id', '')
        self.product_type = kwargs.get('product_type', '')
        self.assigned_date = kwargs.get('assigned_date', '')
        self.expected_completion = kwargs.get('expected_completion', '')
        self.payment_terms = kwargs.get('payment_terms', {})
        self.status = kwargs.get('status', 'assigned')  # assigned, in_progress, completed
        
        # Remove from kwargs to avoid conflicts
        kwargs_copy = kwargs.copy()
        order_attrs = ['order_id', 'artisan_id', 'workshop_id', 'product_type', 
                      'assigned_date', 'expected_completion', 'payment_terms', 'status']
        for key in order_attrs:
            kwargs_copy.pop(key, None)
        
        super().__init__(**kwargs_copy)
    
    @property
    def identifier(self):
        return self.order_id
    
    @property
    def creator(self):
        return getattr(self, 'created_by', 'workshop')
    
    @property
    def type(self):
        return 'work_order'
    
    @property
    def owner(self):
        return self.artisan_id


class BusinessTransaction(CraftloreObject):
    """Business transaction object for blockchain storage."""
    
    def __init__(self, **kwargs):
        # Transaction-specific attributes
        self.transaction_id = kwargs.get('transaction_id', self.generate_unique_identifier())
        self.buyer_id = kwargs.get('buyer_id', '')
        self.seller_id = kwargs.get('seller_id', '')
        self.product_id = kwargs.get('product_id', '')
        self.transaction_type = kwargs.get('transaction_type', 'purchase')  # purchase, sale, transfer
        self.amount = kwargs.get('amount', 0.0)
        self.payment_method = kwargs.get('payment_method', '')
        self.payment_status = kwargs.get('payment_status', 'pending')
        self.royalty_info = kwargs.get('royalty_info', {})
        
        # Remove from kwargs to avoid conflicts
        kwargs_copy = kwargs.copy()
        transaction_attrs = ['transaction_id', 'buyer_id', 'seller_id', 'product_id', 
                           'transaction_type', 'amount', 'payment_method', 'payment_status', 'royalty_info']
        for key in transaction_attrs:
            kwargs_copy.pop(key, None)
        
        super().__init__(**kwargs_copy)
    
    @property
    def identifier(self):
        return self.transaction_id
    
    @property
    def creator(self):
        return self.buyer_id
    
    @property
    def type(self):
        return 'business_transaction'
    
    @property
    def owner(self):
        return self.buyer_id


class Certificate(CraftloreObject):
    """Certificate object for blockchain storage."""
    
    def __init__(self, **kwargs):
        # Certificate-specific attributes
        self.certificate_id = kwargs.get('certificate_id', self.generate_unique_identifier())
        self.certificate_type = kwargs.get('certificate_type', '')  # GI, organic, skill, etc.
        self.holder_id = kwargs.get('holder_id', '')
        self.issuing_authority = kwargs.get('issuing_authority', '')
        self.issue_date = kwargs.get('issue_date', '')
        self.expiry_date = kwargs.get('expiry_date', '')
        self.certificate_data = kwargs.get('certificate_data', {})
        
        # Remove from kwargs to avoid conflicts
        kwargs_copy = kwargs.copy()
        cert_attrs = ['certificate_id', 'certificate_type', 'holder_id', 'issuing_authority', 
                     'issue_date', 'expiry_date', 'certificate_data']
        for key in cert_attrs:
            kwargs_copy.pop(key, None)
        
        super().__init__(**kwargs_copy)
    
    @property
    def identifier(self):
        return self.certificate_id
    
    @property
    def creator(self):
        return self.issuing_authority
    
    @property
    def type(self):
        return 'certificate'
    
    @property
    def owner(self):
        return self.holder_id


# Placeholder implementations for the handler methods
# These would be fully implemented based on specific business logic

def _update_account(self, transaction, context: Context, payload: Dict, signer_id: str, signer_type: AccountType):
    """Update account information."""
    # Implementation placeholder
    pass

def _delete_account(self, transaction, context: Context, payload: Dict, signer_id: str, signer_type: AccountType):
    """Soft delete account."""
    # Implementation placeholder
    pass

# Add all other placeholder implementations...
# (The actual implementations would contain the specific business logic for each operation)

print("🎨 CraftLore Transaction Handlers loaded successfully!")
