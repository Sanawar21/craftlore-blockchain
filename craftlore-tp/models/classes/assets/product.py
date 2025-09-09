from pydantic import Field
from typing import List, Optional

from . import BaseAsset
from models.enums import AssetType, WorkOrderStatus, BatchStatus

# --- Product ---
class Product(BaseAsset):
    """Individual product from a batch."""
    asset_type: AssetType = Field(default=AssetType.PRODUCT)
    batch: str                        # Link to ProductBatch
    serial_no: int                       # Unique within batch
    price_usd: float
    quantity: float 
    unit: str  # e.g. "pieces", "
    packaging: Optional[str] = None         # Link to Packaging