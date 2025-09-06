from .update_email_index import EmailIndexUpdater
from .update_owner_history import OwnerHistoryUpdater
from .update_entity_history import EntityHistoryUpdater
from .update_assignee import AssigneeUpdater
from .update_batch import BatchUpdater

listeners = [
    EmailIndexUpdater,
    OwnerHistoryUpdater,
    EntityHistoryUpdater,
    AssigneeUpdater,
    BatchUpdater,
]