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
    BUYER = "buyer"

class AssetType(BaseEnum):
    RAW_MATERIAL = "raw_material"
    WORK_ORDER = "work_order"
    PRODUCT = "product"
    PRODUCT_BATCH = "product_batch"
    PACKAGING = "packaging"
    LOGISTICS = "logistics"

class EventType(BaseEnum):
    ACCOUNT_CREATED = "create/account"
    ASSET_CREATED = "create/asset"
    ASSETS_TRANSFERRED = "transfer/asset"
    WORK_ORDER_ACCEPTED = "accept/work_order"
    WORK_ORDER_REJECTED = "reject/work_order"
    WORK_ORDER_COMPLETED = "complete/work_order"
    ADD_RAW_MATERIAL = "add/raw_material"
    ADD_SUB_ASSIGNEE = "add/sub_assignee"

class SubEventType(BaseEnum):
    """Sub-event types for more granular event handling."""
    WORK_ORDER_CREATED = "create/asset/work_order"
    PACKAGING_CREATED = "create/asset/packaging"
    BATCH_CREATED = "accept/work_order/batch_created"
    LOGISTICS_CREATED = "create/asset/logistics"


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

class WorkOrderType(BaseEnum):
    PRODUCTION = "production"
    REPAIR = "repair"