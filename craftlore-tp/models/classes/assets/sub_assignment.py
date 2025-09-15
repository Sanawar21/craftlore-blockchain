from pydantic import Field
from typing import List, Optional

from . import BaseAsset
from models.enums import AssetType, SubAssignmentStatus

# TODO: BUG: statuses can be set to anything when creating via payload
# Rejection reason can be set by creator even if not rejected 

# --- SubAssignment ---
class SubAssignment(BaseAsset):
    """Sub-assignment contract for part of a product batch."""
    asset_type: AssetType = Field(default=AssetType.SUB_ASSIGNMENT)
    batch: str                        # Link to ProductBatch
    pay_usd: float
    task_description: str             # Free text (e.g., "knit 50 wool shawls")
    status: SubAssignmentStatus = Field(default=SubAssignmentStatus.PENDING)
    assignee: str                     # Artisan or workshop public key
    assigner: str                     # Producer public key
    rejection_reason: Optional[str] = None # Filled if status is REJECTED