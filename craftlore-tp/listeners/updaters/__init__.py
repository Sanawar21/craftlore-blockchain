from .update_email_index import EmailIndexUpdater
from .update_owner_history import OwnerHistoryUpdater
from .update_entity_history import EntityHistoryUpdater
from .update_assignee import AssigneeUpdater
from .update_batch import BatchUpdater
from .package_products import PackageProducts
from .add_raw_material import AddToBatch
from .transfer_assets import AssetsTransferrer
from .producer_updater import ProducerUpdater
from .update_subassignee import SubAssigneeUpdater
from .delete_entity import DeleteEntity
from .unpack_product import UnpackProduct
from .edit_entity import EditEntity
from .update_admin_actions import AdminActionsUpdater
from .update_holder import CertificateHolderUpdater
from .moderator_edit import ModeratorEdit

listeners = [
    EmailIndexUpdater,
    OwnerHistoryUpdater,
    EntityHistoryUpdater,
    AssigneeUpdater,
    BatchUpdater,
    PackageProducts,
    AddToBatch,
    AssetsTransferrer,
    ProducerUpdater,
    SubAssigneeUpdater,
    DeleteEntity,
    UnpackProduct,
    EditEntity,
    AdminActionsUpdater,
    CertificateHolderUpdater,
    ModeratorEdit,
]