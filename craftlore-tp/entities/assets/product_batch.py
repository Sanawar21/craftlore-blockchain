# !/usr/bin/env python3

# Every product belongs to a batch, which is a collection of identical products made together.
# One batch will only be owned by one account

from typing import Dict, List
from .base_asset import BaseAsset
from core.enums import AssetType, ProductBatchStatus


class ProductBatch(BaseAsset):
    """Product batch asset for CraftLore."""
    
    def __init__(self, asset_id: str, owner: str, timestamp):
        super().__init__(asset_id, owner, AssetType.PRODUCT_BATCH, timestamp)
        self.raw_materials_used = []  # List of raw material IDs used in this batch
        self.order_quantity = 0  # Total number of products in this batch
        self.quantity_unit = ""  # Unit of measurement (e.g., "pieces", "
        self.producer_id = ""  # Workshop or artisan that produced this batch
        self.production_date = ""  # Date when the batch was produced
        self.source_location = ""  # Location where the batch was produced
        self.category = ""
        self.artisans_involved = []
        self.current_quantity = 0
        self.reviews = []
        self.name = ""
        self.description = ""
        self.is_complete = False  # Whether the batch production is complete
        self.work_order_id = ""  # Work order that initiated this batch production
        self.batch_status = ProductBatchStatus.PENDING  # Status of the batch production
        self.quality_control_reports = []  # List of QC reports
        self.gi_certification = ""  # GI (Geographical Indication) certification

    def to_dict(self) -> Dict:
        data = super().to_dict()
        data.update({
            'raw_materials_used': self.raw_materials_used,
            'order_quantity': self.order_quantity,
            'quantity_unit': self.quantity_unit,
            'producer_id': self.producer_id,
            'production_date': self.production_date,
            'source_location': self.source_location,
            'category': self.category,
            'artisans_involved': self.artisans_involved,
            # after the creation of the batch, this quantity will reduce as products are sold.
            'current_quantity': self.current_quantity, # if the Batch is not complete, then this does not matter. 
            'reviews': self.reviews,
            'name': self.name,
            'description': self.description,
            'is_complete': self.is_complete,
            'work_order_id': self.work_order_id,
            'batch_status': self.batch_status.value,
            'quality_control_reports': self.quality_control_reports,
            'gi_certification': self.gi_certification
        })
        return data

    @property
    def uneditable_fields(self) -> List[str]:
        fields = super().uneditable_fields
        fields.extend([
            "work_order_id", "reviews", "current_quantity" 
        ])
        return fields

    @property
    def post_lock_editable_fields(self) -> List[str]:
        """Fields that can be edited after the batch is locked."""
        fields = super().post_lock_editable_fields
        fields.extend([
            'production_date',
            'artisans_involved'
        ])
        return fields
