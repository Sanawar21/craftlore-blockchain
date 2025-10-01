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
    ADMIN = "admin"


class AdminPermissionLevel(BaseEnum):
    MODERATOR = "moderator"
    AUTHENTICATOR = "authenticator"
    SUPER_ADMIN = "super_admin"
    CERTIFIER = "certifier"


class AdminAccountStatus(BaseEnum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DEACTIVATED = "deactivated"


class AssetType(BaseEnum):
    RAW_MATERIAL = "raw_material"
    WORK_ORDER = "work_order"
    PRODUCT = "product"
    PRODUCT_BATCH = "product_batch"
    PACKAGING = "packaging"
    LOGISTICS = "logistics"
    SUB_ASSIGNMENT = "sub_assignment"
    CERTIFICATION = "certification"


class EventType(BaseEnum):
    ACCOUNT_CREATED = "create/account"
    ASSET_CREATED = "create/asset"
    ASSETS_TRANSFERRED = "transfer/asset"
    WORK_ORDER_ACCEPTED = "accept/work_order"
    WORK_ORDER_REJECTED = "reject/work_order"
    WORK_ORDER_COMPLETED = "complete/work_order"
    ADD_RAW_MATERIAL = "add/raw_material"
    SUBASSIGNMENT_ACCEPTED = "accept/sub_assignment"
    SUBASSIGNMENT_REJECTED = "reject/sub_assignment"
    SUBASSIGNMENT_COMPLETED = "complete/sub_assignment"
    SUBASSIGNMENT_MARKED_AS_PAID = "paid/sub_assignment"
    BATCH_COMPLETED = "complete/batch"
    ENTITY_EDITED = "edit/entity"
    ENTITY_DELETED = "delete/entity"
    PRODUCT_UNPACKED = "unpackage/product"
    # admin
    BOOTSTRAP = "bootstrap"
    ADMIN_CREATED = "create/admin"
    CERTIFICATION_ISSUED = "issue/certification"
    EDITED_BY_MODERATOR = "moderate/edit"
    ENTITY_AUTHENTICATED = "authenticate/entity"


class SubEventType(BaseEnum):
    """Sub-event types for more granular event handling."""
    WORK_ORDER_CREATED = "create/asset/work_order"
    PACKAGING_CREATED = "create/asset/packaging"
    BATCH_CREATED = "accept/work_order/batch_created"
    LOGISTICS_CREATED = "create/asset/logistics"
    SUB_ASSIGNMENT_CREATED = "create/asset/sub_assignment"


class ArtisanSkillLevel(BaseEnum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    EXPERT = "expert"


class SubAssignmentStatus(BaseEnum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    COMPLETED = "completed"


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


class BuyerType(BaseEnum):
    END_CUSTOMER = "end_customer"
    WHOLESALER = "wholesaler"
    RETAILER = "retailer"
    DISTRIBUTOR = "distributor"
