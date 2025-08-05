from .base import BaseSubHandler
from sawtooth_sdk.processor.context import Context
from sawtooth_sdk.processor.exceptions import InvalidTransaction
from utils.enums import AccountType, AuthenticationStatus
import json

class CreateAccountSubHandler(BaseSubHandler):
    """Subhandler for creating an account in the account transaction processor."""

    def apply(self, transaction, context: Context, payload: dict):
        """Handle account creation with privacy-first design."""
        # Validate required fields
        required_fields = ['account_type', 'email', "timestamp"]
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