from enum import Enum

class BaseEnum(str, Enum):
    """Base Enum class to ensure string values"""


class AuthenticationStatus(BaseEnum):
    """Accounts authentication status"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class AccountType(BaseEnum):
    SUPPLIER = "supplier"
    ARTISAN = "artisan"

class AssetType(BaseEnum):
    RAW_MATERIAL = "raw_material"
    WORK_ORDER = "work_order"
    PRODUCT = "product"
    PRODUCT_BATCH = "product_batch"

class EventType(BaseEnum):
    ACCOUNT_CREATED = "create/account"
    ACCOUNT_UPDATED = "update/account"
    ACCOUNT_DELETED = "delete/account"
    ASSET_CREATED = "create/asset"
    ASSET_UPDATED = "update/asset"
    ASSET_DELETED = "delete/asset"
    WORK_ORDER_ACCEPTED = "accept/work_order"
    WORK_ORDER_REJECTED = "reject/work_order"
    WORK_ORDER_COMPLETED = "complete/work_order"

class SubEventType(BaseEnum):
    """Sub-event types for more granular event handling."""
    WORK_ORDER_CREATED = "create/asset/work_order"
    BATCH_CREATED = "accept/work_order/batch_created"


class ArtisanSkillLevel(BaseEnum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    EXPERT = "expert"

class WorkOrderStatus(BaseEnum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    COMPLETED = "completed"    
    REJECTED = "rejected"

class BatchStatus(BaseEnum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    PACKAGED = "packaged" # packaging will be done after completion


class WorkOrderType(BaseEnum):
    PRODUCTION = "production"
    REPAIR = "repair"
    