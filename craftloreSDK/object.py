from abc import ABC, abstractmethod
import hashlib
import json
import time
import random
from enum import Enum
from typing import List, Dict, Optional, Set
from datetime import datetime

class AuthenticationStatus(Enum):
    """Authentication status for objects and accounts."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUSPENDED = "suspended"
    REVOKED = "revoked"

class Permission(Enum):
    """Permission types for role-based access control."""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    AUTHENTICATE = "authenticate"
    SUPER_ADMIN = "super_admin"

class AccountType(Enum):
    """Different types of accounts in the system."""
    SUPER_ADMIN = "super_admin"
    ARTISAN_ADMIN = "artisan_admin"
    SUPPLIER_ADMIN = "supplier_admin"
    WORKSHOP_ADMIN = "workshop_admin"
    DISTRIBUTOR_ADMIN = "distributor_admin"
    WHOLESALER_ADMIN = "wholesaler_admin"
    RETAILER_ADMIN = "retailer_admin"
    ARTISAN = "artisan"
    SUPPLIER = "supplier"
    WORKSHOP = "workshop"
    DISTRIBUTOR = "distributor"
    WHOLESALER = "wholesaler"
    RETAILER = "retailer"
    BUYER = "buyer"

class HistoryEntry:
    """Represents a single entry in object history."""
    
    def __init__(self, block_number: int, transaction_id: str, action: str, 
                 actor_id: str, previous_state: Dict, current_state: Dict, 
                 timestamp: Optional[int] = None):
        self.block_number = block_number
        self.transaction_id = transaction_id
        self.action = action  # create, update, delete, authenticate, etc.
        self.actor_id = actor_id  # Who performed the action
        self.previous_state = previous_state
        self.current_state = current_state
        self.timestamp = timestamp or time.time_ns()
    
    def to_dict(self):
        return {
            'block_number': self.block_number,
            'transaction_id': self.transaction_id,
            'action': self.action,
            'actor_id': self.actor_id,
            'previous_state': self.previous_state,
            'current_state': self.current_state,
            'timestamp': self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        return cls(**data)

class AuthenticationEntry:
    """Represents an authentication/approval entry."""
    
    def __init__(self, approver_id: str, status: AuthenticationStatus, 
                 reason: str = "", timestamp: Optional[int] = None):
        self.approver_id = approver_id
        self.status = status
        self.reason = reason
        self.timestamp = timestamp or time.time_ns()
    
    def to_dict(self):
        return {
            'approver_id': self.approver_id,
            'status': self.status.value,
            'reason': self.reason,
            'timestamp': self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        return cls(
            approver_id=data['approver_id'],
            status=AuthenticationStatus(data['status']),
            reason=data.get('reason', ''),
            timestamp=data.get('timestamp')
        )

class CraftloreObject(ABC):
    """
    Base class for all Craftlore objects.
    This class can be extended to create specific types of objects in the Craftlore SDK.
    """
    
    # Default royalty percentage (can be overridden by subclasses)
    DEFAULT_ROYALTY_PERCENTAGE = 5.0
    
    def __init__(self, **kwargs):
        """
        Initialize the Craftlore object with any keyword arguments.
        
        :param kwargs: Arbitrary keyword arguments to initialize the object.
        """
        # Skip abstract properties when setting attributes
        abstract_properties = {'identifier', 'creator', 'type', 'owner'}
        
        # Core object attributes
        for key, value in kwargs.items():
            if key not in abstract_properties:
                setattr(self, key, value)
        
        # Authentication and authorization
        self.authentication_status = AuthenticationStatus.PENDING
        self.authentication_entries: List[AuthenticationEntry] = []
        self.authorized_by: Set[str] = set()  # Account IDs who can authorize this object
        self.required_signatures = kwargs.get('required_signatures', 1)  # Multi-signature support
        
        # Ownership and creation
        self.owner_id = kwargs.get('owner_id', kwargs.get('creator_id', 'unknown'))
        self.created_by = kwargs.get('creator_id', 'unknown')
        self.created_at = kwargs.get('created_at', time.time_ns())
        
        # Soft delete support
        self.is_deleted = False
        self.deleted_at: Optional[int] = None
        self.deleted_by: Optional[str] = None
        
        # History tracking
        self.history: List[HistoryEntry] = []
        self.version = 1
        
        # Blockchain addresses
        self._object_address: Optional[str] = None
        self._history_address: Optional[str] = None 
    
    @property
    @abstractmethod
    def identifier(self):
        """
        Return the unique identifier for the object.
        This property must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    @property
    @abstractmethod
    def creator(self):
        """
        Return the creator of the object.
        This property must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement this method.")
    
    @property
    @abstractmethod
    def type(self):
        """
        Return the type of the object.
        This property must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    @property
    @abstractmethod
    def owner(self):
        """
        Return the owner of the object.
        This property must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    # ========================
    # AUTHORIZATION METHODS
    # ========================
    
    def can_authenticate(self, account_id: str, account_type: AccountType) -> bool:
        """
        Check if an account can authenticate this object based on role hierarchy.
        
        :param account_id: ID of the account requesting authentication
        :param account_type: Type of the account
        :return: True if account can authenticate this object
        """
        # Super admin can authenticate anything
        if account_type == AccountType.SUPER_ADMIN:
            return True
        
        # Object owner can always authenticate their own objects
        if account_id == self.owner_id:
            return True
        
        # Check if account is in authorized_by list
        if account_id in self.authorized_by:
            return True
        
        # Role-based authentication rules
        object_type = self.type.lower()
        
        # For account objects, check if the admin can manage this type
        if object_type == 'account':
            # Get the specific account type from the object
            target_account_type = getattr(self, 'account_type', None)
            if target_account_type:
                # Artisan Admin can authenticate artisan accounts
                if account_type == AccountType.ARTISAN_ADMIN and target_account_type == AccountType.ARTISAN:
                    return True
                
                # Supplier Admin can authenticate supplier accounts
                if account_type == AccountType.SUPPLIER_ADMIN and target_account_type == AccountType.SUPPLIER:
                    return True
                
                # Workshop Admin can authenticate workshop accounts
                if account_type == AccountType.WORKSHOP_ADMIN and target_account_type == AccountType.WORKSHOP:
                    return True
                
                # Distributor Admin can authenticate distributor accounts
                if account_type == AccountType.DISTRIBUTOR_ADMIN and target_account_type == AccountType.DISTRIBUTOR:
                    return True
                
                # Wholesaler Admin can authenticate wholesaler accounts
                if account_type == AccountType.WHOLESALER_ADMIN and target_account_type == AccountType.WHOLESALER:
                    return True
                
                # Retailer Admin can authenticate retailer accounts
                if account_type == AccountType.RETAILER_ADMIN and target_account_type == AccountType.RETAILER:
                    return True
        
        # For product objects, artisan admin can authenticate artisan products
        elif 'product' in object_type or 'artisan' in object_type:
            if account_type == AccountType.ARTISAN_ADMIN:
                return True
        
        # For supplier objects, supplier admin can authenticate
        elif 'supplier' in object_type or 'material' in object_type:
            if account_type == AccountType.SUPPLIER_ADMIN:
                return True
        
        # For workshop objects, workshop admin can authenticate
        elif 'workshop' in object_type:
            if account_type == AccountType.WORKSHOP_ADMIN:
                return True
        
        return False
    
    def can_modify(self, account_id: str, account_type: AccountType) -> bool:
        """
        Check if an account can modify (update/delete) this object.
        
        :param account_id: ID of the account requesting modification
        :param account_type: Type of the account
        :return: True if account can modify this object
        """
        # Super admin can modify anything
        if account_type == AccountType.SUPER_ADMIN:
            return True
        
        # Only object owner can modify (unless deleted)
        if account_id == self.owner_id and not self.is_deleted:
            return True
        
        return False
    
    def authenticate(self, approver_id: str, account_type: AccountType, 
                    status: AuthenticationStatus, reason: str = "", 
                    block_number: int = 0, transaction_id: str = "") -> bool:
        """
        Authenticate this object with multi-signature support.
        
        :param approver_id: ID of the account approving
        :param account_type: Type of the approving account
        :param status: New authentication status
        :param reason: Reason for authentication decision
        :param block_number: Blockchain block number
        :param transaction_id: Transaction ID
        :return: True if authentication successful
        """
        if not self.can_authenticate(approver_id, account_type):
            raise PermissionError(f"Account {approver_id} cannot authenticate this object")
        
        # Record current state before change
        previous_state = self.to_dict()
        
        # Add authentication entry
        auth_entry = AuthenticationEntry(approver_id, status, reason)
        self.authentication_entries.append(auth_entry)
        
        # Count signatures for this status
        signatures_count = sum(1 for entry in self.authentication_entries 
                             if entry.status == status)
        
        # Update authentication status if enough signatures
        if signatures_count >= self.required_signatures:
            self.authentication_status = status
        
        # Record history
        current_state = self.to_dict()
        history_entry = HistoryEntry(
            block_number=block_number,
            transaction_id=transaction_id,
            action=f"authenticate_{status.value}",
            actor_id=approver_id,
            previous_state=previous_state,
            current_state=current_state
        )
        self.history.append(history_entry)
        
        return True
    
    def transfer_ownership(self, new_owner_id: str, authorized_by: str, 
                          account_type: AccountType, block_number: int = 0, 
                          transaction_id: str = "") -> bool:
        """
        Transfer ownership of this object.
        
        :param new_owner_id: ID of the new owner
        :param authorized_by: ID of the account authorizing transfer
        :param account_type: Type of the authorizing account
        :param block_number: Blockchain block number
        :param transaction_id: Transaction ID
        :return: True if transfer successful
        """
        if not self.can_modify(authorized_by, account_type):
            raise PermissionError(f"Account {authorized_by} cannot transfer ownership")
        
        # Record current state before change
        previous_state = self.to_dict()
        
        # Update ownership
        old_owner = self.owner_id
        self.owner_id = new_owner_id
        
        # Record history
        current_state = self.to_dict()
        history_entry = HistoryEntry(
            block_number=block_number,
            transaction_id=transaction_id,
            action="transfer_ownership",
            actor_id=authorized_by,
            previous_state=previous_state,
            current_state=current_state
        )
        self.history.append(history_entry)
        
        return True
    
    def soft_delete(self, deleted_by: str, account_type: AccountType, 
                   block_number: int = 0, transaction_id: str = "") -> bool:
        """
        Soft delete this object.
        
        :param deleted_by: ID of the account performing deletion
        :param account_type: Type of the deleting account
        :param block_number: Blockchain block number
        :param transaction_id: Transaction ID
        :return: True if deletion successful
        """
        if not self.can_modify(deleted_by, account_type):
            raise PermissionError(f"Account {deleted_by} cannot delete this object")
        
        if self.is_deleted:
            return False  # Already deleted
        
        # Record current state before change
        previous_state = self.to_dict()
        
        # Mark as deleted
        self.is_deleted = True
        self.deleted_at = time.time_ns()
        self.deleted_by = deleted_by
        
        # Record history
        current_state = self.to_dict()
        history_entry = HistoryEntry(
            block_number=block_number,
            transaction_id=transaction_id,
            action="soft_delete",
            actor_id=deleted_by,
            previous_state=previous_state,
            current_state=current_state
        )
        self.history.append(history_entry)
        
        return True
    
    def update_object(self, updated_by: str, account_type: AccountType, 
                     updates: Dict, block_number: int = 0, 
                     transaction_id: str = "") -> bool:
        """
        Update object attributes.
        
        :param updated_by: ID of the account performing update
        :param account_type: Type of the updating account
        :param updates: Dictionary of updates to apply
        :param block_number: Blockchain block number
        :param transaction_id: Transaction ID
        :return: True if update successful
        """
        if not self.can_modify(updated_by, account_type):
            raise PermissionError(f"Account {updated_by} cannot update this object")
        
        if self.is_deleted:
            raise ValueError("Cannot update deleted object")
        
        # Record current state before change
        previous_state = self.to_dict()
        
        # Apply updates
        for key, value in updates.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        # Increment version
        self.version += 1
        
        # Record history
        current_state = self.to_dict()
        history_entry = HistoryEntry(
            block_number=block_number,
            transaction_id=transaction_id,
            action="update",
            actor_id=updated_by,
            previous_state=previous_state,
            current_state=current_state
        )
        self.history.append(history_entry)
        
        return True
    
    # ========================
    # BLOCKCHAIN ADDRESS METHODS
    # ========================
    
    def get_object_address(self) -> str:
        """Get the blockchain address for storing this object."""
        if self._object_address is None:
            self._object_address = self._generate_object_address()
        return self._object_address
    
    def get_history_address(self) -> str:
        """Get the blockchain address for storing this object's history."""
        if self._history_address is None:
            self._history_address = self._generate_history_address()
        return self._history_address
    
    def _generate_object_address(self) -> str:
        """Generate blockchain address for object storage."""
        return hashlib.sha512(
            (f"obj_{self.type}_{self.identifier}").encode('utf-8')
        ).hexdigest()[:70]
    
    def _generate_history_address(self) -> str:
        """Generate blockchain address for history storage."""
        return hashlib.sha512(
            (f"hist_{self.type}_{self.identifier}").encode('utf-8')
        ).hexdigest()[:70]

    # ========================
    # SERIALIZATION METHODS
    # ========================

    def to_json(self):
        """
        Convert the Craftlore object to a JSON string.
        
        :return: JSON string representation of the object.
        """
        return json.dumps(self.to_dict(), indent=4, default=str)
    
    def to_dict(self):
        """
        Convert the Craftlore object to a dictionary.
        
        :return: Dictionary representation of the object.
        """
        obj_dict = {}
        for key, value in self.__dict__.items():
            if key.startswith('_'):  # Skip private attributes
                continue
            
            if isinstance(value, Enum):
                obj_dict[key] = value.value
            elif isinstance(value, set):
                obj_dict[key] = list(value)
            elif isinstance(value, list):
                if value and hasattr(value[0], 'to_dict'):
                    obj_dict[key] = [item.to_dict() for item in value]
                else:
                    obj_dict[key] = value
            elif hasattr(value, 'to_dict'):
                obj_dict[key] = value.to_dict()
            else:
                obj_dict[key] = value
        
        return obj_dict

    @classmethod
    def from_json(cls, data):
        """
        Create a Craftlore object from a JSON string.
        
        :param data: JSON string representing the object.
        :return: Instance of the Craftlore object.
        """
        obj_data = json.loads(data)
        return cls.from_dict(obj_data)

    @classmethod
    def from_dict(cls, data):
        """
        Create a Craftlore object from a dictionary.
        
        :param data: Dictionary representing the object.
        :return: Instance of the Craftlore object.
        """
        # Handle enum conversions
        if 'authentication_status' in data:
            data['authentication_status'] = AuthenticationStatus(data['authentication_status'])
        
        # Handle authentication entries
        if 'authentication_entries' in data:
            data['authentication_entries'] = [
                AuthenticationEntry.from_dict(entry) for entry in data['authentication_entries']
            ]
        
        # Handle history entries
        if 'history' in data:
            data['history'] = [
                HistoryEntry.from_dict(entry) for entry in data['history']
            ]
        
        # Handle sets
        if 'authorized_by' in data:
            data['authorized_by'] = set(data['authorized_by'])
        
        return cls(**data)

    @classmethod
    def new(cls, **kwargs):
        """
        Create a new instance of the Craftlore object.
        
        :param kwargs: Arbitrary keyword arguments to initialize the object.
        :return: New instance of the Craftlore object.
        """
        # Generate unique identifier if not provided
        if 'identifier' not in kwargs:
            timestamp = time.time_ns()
            kwargs['identifier'] = cls.generate_unique_identifier(timestamp)
        
        # Set creation timestamp if not provided
        if 'created_at' not in kwargs:
            kwargs['created_at'] = time.time_ns()
        
        return cls(**kwargs)

    def __repr__(self):
        """
        Return a string representation of the Craftlore object.
        
        :return: String representation of the object.
        """
        return f"{self.__class__.__name__}(id={self.identifier}, type={self.type}, status={self.authentication_status.value})"

    @staticmethod
    def generate_unique_identifier(timestamp=None):
        """
        Generate a unique identifier using hash of current timestamp in nanoseconds and a random number.
        
        :return: Hexadecimal string identifier.
        """
        if timestamp is None:
            timestamp_ns = time.time_ns()
        else:
            timestamp_ns = timestamp

        # Generate a random number for additional uniqueness
        random_num = random.randint(1000000, 9999999)
        
        # Combine timestamp and random number
        combined_data = f"{timestamp_ns}{random_num}"
        
        # Create SHA-256 hash
        hash_object = hashlib.sha256(combined_data.encode('utf-8'))
        
        # Return the hexadecimal representation (first 32 characters for reasonable length)
        return hash_object.hexdigest()[:32]