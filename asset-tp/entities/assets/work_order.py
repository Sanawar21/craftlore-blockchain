#!/usr/bin/env python3

from typing import Dict, List
from .base_asset import BaseAsset
from core.enums import AssetType, WorkOrderStatus


class WorkOrder(BaseAsset):
    """Work order asset for CraftLore."""
    
    def __init__(self, asset_id: str, public_key: str, timestamp):
        super().__init__(asset_id, public_key, AssetType.RAW_MATERIAL, timestamp)
        self.batch_id = ""
        self.assigner_id = ""  # ID of the account that created this work order
        self.assignee_id = ""  # ID of the account assigned to fulfill this work order
        self.status = WorkOrderStatus.PENDING
        self.assignee_signature = ""  # Signature of the assigned account


    def to_dict(self) -> Dict:
        data = super().to_dict()
        data.update({
            'batch_id': self.batch_id,
            'assigner_id': self.assigner_id,
            'assignee_id': self.assignee_id,
            'status': self.status.value,
            'assignee_signature': self.assignee_signature
        })
        return data

    @property
    def uneditable_fields(self) -> List[str]:
        fields = super().uneditable_fields
        fields.extend([
            "batch_id", "assignee_id", "status"
        ])
        return fields
    
    @property
    def post_lock_fields(self) -> List[str]:
        fields = super().post_lock_fields
        fields.extend([
            "assignee_signature",
            "status",
        ])
        return fields