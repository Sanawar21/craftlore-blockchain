#!/usr/bin/env python3
"""
Account state updater for Asset TP.

This module provides functionality to update account information in account-tp state
when asset operations are performed, ensuring consistency between both transaction processors.
"""

from typing import Dict, List, Optional
from sawtooth_sdk.processor.context import Context
from sawtooth_sdk.processor.exceptions import InvalidTransaction

# Import account-tp utilities
from accountTPutils.address_generator import AccountAddressGenerator
from accountTPutils.serialization import SerializationHelper


class AccountStateUpdater:
    """Updates account state to maintain consistency with asset operations."""
    
    def __init__(self):
        self.account_address_generator = AccountAddressGenerator()
        self.account_serializer = SerializationHelper()
    
    def get_account_by_public_key(self, context: Context, public_key: str) -> Optional[Dict]:
        """Get account information by public key from account-tp state."""
        try:
            account_address = self.account_address_generator.generate_account_address(public_key)
            entries = context.get_state([account_address])
            
            if entries:
                return self.account_serializer.from_bytes(entries[0].data)
            return None
        except Exception as e:
            print(f"Warning: Could not retrieve account for {public_key}: {str(e)}")
            return None
    
    def update_account(self, context: Context, account_data: Dict) -> None:
        """Update account data in account-tp state."""
        try:
            public_key = account_data['public_key']
            account_address = self.account_address_generator.generate_account_address(public_key)
            
            context.set_state({
                account_address: self.account_serializer.to_bytes(account_data)
            })
        except Exception as e:
            print(f"Warning: Could not update account for {account_data.get('public_key')}: {str(e)}")
    
    def add_account_history(self, account_data: Dict, history_entry: Dict, timestamp: str) -> None:
        """Add history entry to account."""
        if 'history' not in account_data:
            account_data['history'] = []
        
        history_entry['timestamp'] = timestamp
        account_data['history'].append(history_entry)
        account_data['updated_timestamp'] = timestamp
    
    def update_supplier_raw_materials(self, context: Context, supplier_public_key: str, 
                                    raw_material_id: str, operation: str, timestamp: str) -> None:
        """Update supplier account when raw materials are created or transferred."""
        account = self.get_account_by_public_key(context, supplier_public_key)
        if not account:
            print(f"Warning: Supplier account not found: {supplier_public_key}")
            return
        
        if operation == 'created':
            # Add raw material to supplier's list if not already present
            if 'raw_materials_supplied' not in account:
                account['raw_materials_supplied'] = []
            
            if raw_material_id not in account['raw_materials_supplied']:
                account['raw_materials_supplied'].append(raw_material_id)
            
            # Add history entry
            self.add_account_history(account, {
                'action': 'raw_material_created',
                'asset_id': raw_material_id,
                'details': f'Created raw material: {raw_material_id}'
            }, timestamp)
            
        elif operation == 'transferred':
            # Add history entry for transfer
            self.add_account_history(account, {
                'action': 'raw_material_transferred',
                'asset_id': raw_material_id,
                'details': f'Transferred raw material: {raw_material_id}'
            }, timestamp)
        
        self.update_account(context, account)
    
    def update_artisan_work_orders(self, context: Context, artisan_public_key: str, 
                                 work_order_id: str, operation: str, timestamp: str) -> None:
        """Update artisan account when work orders are assigned or completed."""
        account = self.get_account_by_public_key(context, artisan_public_key)
        if not account:
            print(f"Warning: Artisan account not found: {artisan_public_key}")
            return
        
        if operation == 'assigned':
            # Add work order to artisan's list if not already present
            if 'work_orders_assigned' not in account:
                account['work_orders_assigned'] = []
            
            if work_order_id not in account['work_orders_assigned']:
                account['work_orders_assigned'].append(work_order_id)
            
            # Add history entry
            self.add_account_history(account, {
                'action': 'work_order_assigned',
                'asset_id': work_order_id,
                'details': f'Assigned work order: {work_order_id}'
            }, timestamp)
            
        elif operation == 'accepted':
            # Add history entry for acceptance
            self.add_account_history(account, {
                'action': 'work_order_accepted',
                'asset_id': work_order_id,
                'details': f'Accepted work order: {work_order_id}'
            }, timestamp)
            
        elif operation == 'completed':
            # Update performance metrics
            if 'performance_metrics' not in account:
                account['performance_metrics'] = {'products_completed': 0}
            
            account['performance_metrics']['products_completed'] += 1
            
            # Add history entry
            self.add_account_history(account, {
                'action': 'work_order_completed',
                'asset_id': work_order_id,
                'details': f'Completed work order: {work_order_id}'
            }, timestamp)
        
        self.update_account(context, account)
    
    def update_buyer_products(self, context: Context, buyer_public_key: str, 
                            product_ids: List[str], operation: str, timestamp: str) -> None:
        """Update buyer account when products are purchased or transferred."""
        account = self.get_account_by_public_key(context, buyer_public_key)
        if not account:
            print(f"Warning: Buyer account not found: {buyer_public_key}")
            return
        
        if operation == 'purchased':
            # Add products to buyer's list
            if 'products_owned' not in account:
                account['products_owned'] = []
            
            for product_id in product_ids:
                if product_id not in account['products_owned']:
                    account['products_owned'].append(product_id)
            
            # Add history entry
            self.add_account_history(account, {
                'action': 'products_purchased',
                'asset_ids': product_ids,
                'details': f'Purchased {len(product_ids)} products'
            }, timestamp)
            
        elif operation == 'transferred':
            # Remove products from buyer's list
            if 'products_owned' in account:
                for product_id in product_ids:
                    if product_id in account['products_owned']:
                        account['products_owned'].remove(product_id)
            
            # Add history entry
            self.add_account_history(account, {
                'action': 'products_transferred',
                'asset_ids': product_ids,
                'details': f'Transferred {len(product_ids)} products'
            }, timestamp)
        
        self.update_account(context, account)
    
    def update_retailer_inventory(self, context: Context, retailer_public_key: str, 
                                product_ids: List[str], operation: str, timestamp: str) -> None:
        """Update retailer account when inventory changes."""
        account = self.get_account_by_public_key(context, retailer_public_key)
        if not account:
            print(f"Warning: Retailer account not found: {retailer_public_key}")
            return
        
        if operation == 'received':
            # Add products to retailer's inventory
            if 'products_in_stock' not in account:
                account['products_in_stock'] = []
            
            for product_id in product_ids:
                if product_id not in account['products_in_stock']:
                    account['products_in_stock'].append(product_id)
            
            # Add inventory record
            if 'inventory_records' not in account:
                account['inventory_records'] = []
            
            account['inventory_records'].append({
                'operation': 'received',
                'product_ids': product_ids,
                'timestamp': timestamp
            })
            
            # Add history entry
            self.add_account_history(account, {
                'action': 'inventory_received',
                'asset_ids': product_ids,
                'details': f'Received {len(product_ids)} products in inventory'
            }, timestamp)
            
        elif operation == 'sold':
            # Remove products from retailer's inventory
            if 'products_in_stock' in account:
                for product_id in product_ids:
                    if product_id in account['products_in_stock']:
                        account['products_in_stock'].remove(product_id)
            
            # Add inventory record
            if 'inventory_records' not in account:
                account['inventory_records'] = []
            
            account['inventory_records'].append({
                'operation': 'sold',
                'product_ids': product_ids,
                'timestamp': timestamp
            })
            
            # Add history entry
            self.add_account_history(account, {
                'action': 'inventory_sold',
                'asset_ids': product_ids,
                'details': f'Sold {len(product_ids)} products from inventory'
            }, timestamp)
        
        self.update_account(context, account)
    
    def update_workshop_production(self, context: Context, workshop_public_key: str, 
                                 work_order_id: str, product_batch_id: str, operation: str, timestamp: str) -> None:
        """Update workshop account when production activities occur."""
        account = self.get_account_by_public_key(context, workshop_public_key)
        if not account:
            print(f"Warning: Workshop account not found: {workshop_public_key}")
            return
        
        if operation == 'work_order_issued':
            # Add to work orders issued
            if 'work_orders_issued' not in account:
                account['work_orders_issued'] = []
            
            if work_order_id not in account['work_orders_issued']:
                account['work_orders_issued'].append(work_order_id)
            
            # Add history entry
            self.add_account_history(account, {
                'action': 'work_order_issued',
                'asset_id': work_order_id,
                'details': f'Issued work order: {work_order_id}'
            }, timestamp)
            
        elif operation == 'production_completed':
            # Add to products produced
            if 'products_produced' not in account:
                account['products_produced'] = []
            
            if product_batch_id not in account['products_produced']:
                account['products_produced'].append(product_batch_id)
            
            # Update performance metrics
            if 'performance_metrics' not in account:
                account['performance_metrics'] = {'batches_completed': 0}
            
            account['performance_metrics']['batches_completed'] = account['performance_metrics'].get('batches_completed', 0) + 1
            
            # Add history entry
            self.add_account_history(account, {
                'action': 'production_completed',
                'asset_id': product_batch_id,
                'work_order_id': work_order_id,
                'details': f'Completed production of batch: {product_batch_id}'
            }, timestamp)
        
        self.update_account(context, account)
