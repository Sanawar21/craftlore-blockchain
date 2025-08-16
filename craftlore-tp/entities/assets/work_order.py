#!/usr/bin/env python3

from .base_asset import BaseAsset
from core.enums import AssetType, WorkOrderStatus
from typing import Dict, List


class WorkOrder(BaseAsset):
    """Work order asset for CraftLore."""
    
    def __init__(self, asset_id: str, public_key: str, timestamp):
        super().__init__(asset_id, public_key, AssetType.WORK_ORDER, timestamp)
        self.batch_id = ""
        self.assigner_id = ""  # ID of the account that created this work order
        self.assignee_id = ""  # ID of the account assigned to fulfill this work order (primary assignee)
        self.status = WorkOrderStatus.PENDING
        self.assignee_signature = ""  # Signature of the assigned account
        self.rejection_reason = ""  # Reason for rejection if status is REJECTED
        self.work_type = "production"  # production, repair, certification
        self.estimated_completion_date = ""
        self.actual_completion_date = ""
        self.order_quantity = 0  # Number of items/products requested in this work order
        
        # Sub-assignment tracking for workshop → artisan delegation
        self.sub_assignees = []  # List of artisan public keys working on this order
        self.sub_assignment_details = {}  # Dict mapping artisan_id to assignment details
        self.is_sub_assigned = False  # Flag indicating if work has been delegated


    def to_dict(self):
        data = super().to_dict()
        data.update({
            "batch_id": self.batch_id,
            "assigner_id": self.assigner_id,
            "assignee_id": self.assignee_id,
            "status": self.status.value,
            "assignee_signature": self.assignee_signature,
            "rejection_reason": self.rejection_reason,
            "work_type": self.work_type,
            "estimated_completion_date": self.estimated_completion_date,
            "actual_completion_date": self.actual_completion_date,
            "order_quantity": self.order_quantity,
            "sub_assignees": self.sub_assignees,
            "sub_assignment_details": self.sub_assignment_details,
            "is_sub_assigned": self.is_sub_assigned
        })
        return data

    @classmethod
    def from_dict(cls, data):
        # Create instance
        instance = cls(data['asset_id'], data['public_key'], data['timestamp'])
        
        # Set all fields
        for field in ['batch_id', 'assigner_id', 'assignee_id', 'assignee_signature', 
                      'rejection_reason', 'work_type', 'estimated_completion_date', 
                      'actual_completion_date', 'order_quantity', 'sub_assignees', 
                      'sub_assignment_details', 'is_sub_assigned']:
            if field in data:
                setattr(instance, field, data[field])
        
        # Handle enum status
        if 'status' in data:
            instance.status = WorkOrderStatus(data['status'])
        
        # Set inherited fields
        instance.locked = data.get('locked', False)
        instance.locked_by = data.get('locked_by', '')
        
        return instance
    
    def editable_fields(self) -> List[str]:
        return ['batch_id', 'assignee_id', 'status', 'assignee_signature', 
                'rejection_reason', 'work_type', 'estimated_completion_date', 
                'actual_completion_date', 'order_quantity', 'sub_assignees', 
                'sub_assignment_details', 'is_sub_assigned']

    def uneditable_fields(self) -> List[str]:
        return ['assigner_id']

    def post_lock_editable_fields(self) -> List[str]:
        """Fields that can be edited even after the work order is locked"""
        return ['status', 'assignee_signature', 'rejection_reason', 
                'actual_completion_date', 'sub_assignees', 'sub_assignment_details', 
                'is_sub_assigned']