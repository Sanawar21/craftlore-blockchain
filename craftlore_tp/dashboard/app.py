#!/usr/bin/env python3
"""
CraftLore GUI Application
A Flask web interface for CraftLore blockchain interactions.
Combines read_client.py and craftlore_client.py functionality.
"""

import os
import sys
import json
import base64
import hashlib
import requests
from datetime import datetime, timezone
from typing import Dict, Optional
from flask import Flask, render_template, request, jsonify, session, redirect, url_for

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tests.craftlore_client import CraftLoreClient
from utils.serialization import SerializationHelper
from utils.address_generator import CraftLoreAddressGenerator
from models.enums import AccountType, AssetType, EventType, ArtisanSkillLevel, AdminPermissionLevel, WorkOrderType

app = Flask(__name__)
app.secret_key = 'craftlore-gui-secret-key-change-in-production'

# Configuration
REST_API_URL = "http://rest-api:8008"
# REST_API_URL = "http://localhost:8008"

# Initialize utilities
address_generator = CraftLoreAddressGenerator()
serializer = SerializationHelper()

# =============================================
# ROUTES
# =============================================

@app.route('/')
def index():
    """Main dashboard page."""
    return render_template('gui_index.html')

@app.route('/read')
def read_interface():
    """Read client interface."""
    return render_template('gui_read.html')

@app.route('/client')
def client_interface():
    """CraftLore client interface."""
    return render_template('gui_client.html')

# =============================================
# READ CLIENT API ENDPOINTS
# =============================================

def get_state(address):
    """Get state data from blockchain."""
    try:
        url = f"{REST_API_URL}/state/{address}"
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if 'data' in data:
                return base64.b64decode(data['data'])
    except Exception as e:
        print(f"Error getting state: {e}")
    return None

@app.route('/api/read/account_by_pubkey', methods=['POST'])
def read_account_by_pubkey():
    """Query account by public key."""
    try:
        pubkey = request.json.get('public_key', '').strip()
        if not pubkey:
            return jsonify({'error': 'Public key is required'})
        
        address = address_generator.generate_account_address(pubkey)
        data = get_state(address)
        
        if data:
            try:
                obj = json.loads(data.decode(errors='ignore'))
                return jsonify({'success': True, 'data': obj, 'raw_data': data.decode(errors='ignore')})
            except Exception:
                return jsonify({'success': True, 'data': None, 'raw_data': data.decode(errors='ignore')})
        else:
            return jsonify({'error': 'No account found for this public key'})
    except Exception as e:
        return jsonify({'error': f'Error querying account: {str(e)}'})

@app.route('/api/read/account_by_email', methods=['POST'])
def read_account_by_email():
    """Query account by email."""
    try:
        email = request.json.get('email', '').strip()
        if not email:
            return jsonify({'error': 'Email is required'})
        
        address = address_generator.generate_email_index_address(email)
        data = get_state(address)
        
        if data:
            try:
                obj = json.loads(data.decode(errors='ignore'))
                result = {'success': True, 'email_index': obj}
                
                # Get the actual account if public key exists
                if 'public_key' in obj:
                    account_address = address_generator.generate_account_address(obj['public_key'])
                    account_data = get_state(account_address)
                    if account_data:
                        try:
                            account_obj = json.loads(account_data.decode(errors='ignore'))
                            result['account_data'] = account_obj
                        except Exception:
                            result['account_raw'] = account_data.decode(errors='ignore')
                
                return jsonify(result)
            except Exception:
                return jsonify({'success': True, 'email_index': None, 'raw_data': data.decode(errors='ignore')})
        else:
            return jsonify({'error': 'No account found for this email'})
    except Exception as e:
        return jsonify({'error': f'Error querying account: {str(e)}'})

@app.route('/api/read/asset', methods=['POST'])
def read_asset():
    """Query asset by ID."""
    try:
        asset_id = request.json.get('asset_id', '').strip()
        if not asset_id:
            return jsonify({'error': 'Asset ID is required'})
        
        address = address_generator.generate_asset_address(asset_id)
        data = get_state(address)
        
        if data:
            try:
                obj = json.loads(data.decode(errors='ignore'))
                return jsonify({'success': True, 'data': obj, 'raw_data': data.decode(errors='ignore')})
            except Exception:
                return jsonify({'success': True, 'data': None, 'raw_data': data.decode(errors='ignore')})
        else:
            return jsonify({'error': f'No asset found with ID {asset_id}'})
    except Exception as e:
        return jsonify({'error': f'Error querying asset: {str(e)}'})

@app.route('/api/read/transaction', methods=['POST'])
def read_transaction():
    """Query transaction by signature."""
    try:
        txn_sig = request.json.get('transaction_signature', '').strip()
        if not txn_sig:
            return jsonify({'error': 'Transaction signature is required'})
        
        url = f"{REST_API_URL}/transactions/{txn_sig}"
        resp = requests.get(url, timeout=10)
        
        if resp.status_code == 200:
            txn = resp.json().get("data", {})
            header = txn.get("header", {})
            payload_b64 = txn.get("payload", "")
            
            # signer public key
            signer_pubkey = header.get("signer_public_key", "N/A")
            
            # decode payload
            try:
                decoded = base64.b64decode(payload_b64).decode("utf-8")
                payload = json.loads(decoded)
            except Exception:
                payload = decoded  # fallback: raw string
            
            return jsonify({
                'success': True,
                'transaction': txn,
                'decoded_payload': payload,
                'signer_public_key': signer_pubkey
            })
        else:
            return jsonify({'error': f'Failed to fetch transaction. HTTP {resp.status_code}'})
    except Exception as e:
        return jsonify({'error': f'Error querying transaction: {str(e)}'})

@app.route('/api/read/all_state', methods=['GET'])
def read_all_state():
    """List all state entries."""
    try:
        url = f"{REST_API_URL}/state?address={address_generator.FAMILY_NAMESPACE}"
        resp = requests.get(url, timeout=30)
        
        if resp.status_code == 200:
            entries = resp.json().get('data', [])
            processed_entries = []
            
            for entry in entries:
                addr = entry['address']
                data = base64.b64decode(entry['data'])
                
                try:
                    obj = json.loads(data.decode(errors='ignore'))
                    processed_entries.append({
                        'address': addr,
                        'data': obj,
                        'raw_data': data.decode(errors='ignore')
                    })
                except Exception:
                    processed_entries.append({
                        'address': addr,
                        'data': None,
                        'raw_data': data.decode(errors='ignore')
                    })
            
            return jsonify({'success': True, 'entries': processed_entries, 'total': len(entries)})
        else:
            return jsonify({'error': 'Failed to fetch state entries'})
    except Exception as e:
        return jsonify({'error': f'Error fetching state: {str(e)}'})

# =============================================
# CRAFTLORE CLIENT API ENDPOINTS
# =============================================

@app.route('/api/client/create_account', methods=['POST'])
def client_create_account():
    """Create a new account."""
    try:
        data = request.json
        account_type = data.get('account_type')
        email = data.get('email')
        private_key = data.get('private_key')
        
        if not all([account_type, email]):
            return jsonify({'error': 'Account type and email are required'})
        
        # Convert string to enum
        try:
            account_type_enum = AccountType(account_type)
        except ValueError:
            return jsonify({'error': f'Invalid account type: {account_type}'})
        
        # Create client
        client = CraftLoreClient(base_url=REST_API_URL, private_key=private_key)
        
        # Prepare additional fields
        additional_fields = {k: v for k, v in data.items() if k not in ['account_type', 'email', 'private_key']}
        
        # Create account
        result = client.create_account(account_type_enum, email, **additional_fields)
        
        if result.get('status') == 'success':
            return jsonify({
                'success': True,
                'message': 'Account created successfully!',
                'public_key': client.public_key,
                'private_key': client.private_key.as_hex(),
                'batch_link': result.get('link')
            })
        else:
            return jsonify({'error': f"Failed to create account: {result.get('message', result.get('error', 'Unknown error'))}"})
    
    except Exception as e:
        return jsonify({'error': f'Error creating account: {str(e)}'})

@app.route('/api/client/create_asset', methods=['POST'])
def client_create_asset():
    """Create a new asset."""
    try:
        data = request.json
        asset_type = data.get('asset_type')
        private_key = data.get('private_key')
        
        if not all([asset_type, private_key]):
            return jsonify({'error': 'Asset type and private key are required'})
        
        # Convert string to enum
        try:
            asset_type_enum = AssetType(asset_type)
        except ValueError:
            return jsonify({'error': f'Invalid asset type: {asset_type}'})
        
        # Create client
        client = CraftLoreClient(base_url=REST_API_URL, private_key=private_key)
        
        # Prepare asset fields
        asset_fields = {k: v for k, v in data.items() if k not in ['asset_type', 'private_key']}
        
        # Create asset
        result = client.create_asset(asset_type_enum, **asset_fields)
        
        if result.get('status') == 'success':
            return jsonify({
                'success': True,
                'message': 'Asset created successfully!',
                'asset_id': result.get('uid'),
                'batch_link': result.get('link')
            })
        else:
            return jsonify({'error': f"Failed to create asset: {result.get('message', result.get('error', 'Unknown error'))}"})
    
    except Exception as e:
        return jsonify({'error': f'Error creating asset: {str(e)}'})

@app.route('/api/client/transfer_assets', methods=['POST'])
def client_transfer_assets():
    """Transfer assets."""
    try:
        data = request.json
        asset_ids = data.get('asset_ids', [])
        recipient = data.get('recipient')
        private_key = data.get('private_key')
        
        if not all([asset_ids, recipient, private_key]):
            return jsonify({'error': 'Asset IDs, recipient, and private key are required'})
        
        # Create client
        client = CraftLoreClient(base_url=REST_API_URL, private_key=private_key)
        
        # Prepare logistics data
        logistics = {k: v for k, v in data.items() if k not in ['asset_ids', 'recipient', 'private_key']}
        
        # Add required logistics fields if not present
        if 'carrier' not in logistics:
            logistics['carrier'] = data.get('carrier', 'Default Carrier')
        if 'origin' not in logistics:
            logistics['origin'] = data.get('origin', 'Origin Location')
        if 'destination' not in logistics:
            logistics['destination'] = data.get('destination', 'Destination Location')
        if 'dispatch_date' not in logistics:
            logistics['dispatch_date'] = datetime.now(timezone.utc).isoformat()
        
        # Transfer assets
        result = client.transfer_assets(asset_ids, recipient, logistics)
        
        if result.get('status') == 'success':
            return jsonify({
                'success': True,
                'message': 'Assets transferred successfully!',
                'transfer_id': result.get('uid'),
                'batch_link': result.get('link')
            })
        else:
            return jsonify({'error': f"Failed to transfer assets: {result.get('message', result.get('error', 'Unknown error'))}"})
    
    except Exception as e:
        return jsonify({'error': f'Error transferring assets: {str(e)}'})

@app.route('/api/client/work_order_action', methods=['POST'])
def client_work_order_action():
    """Handle work order actions (accept, reject, complete)."""
    try:
        data = request.json
        action = data.get('action')
        work_order_id = data.get('work_order_id')
        private_key = data.get('private_key')
        
        if not all([action, work_order_id, private_key]):
            return jsonify({'error': 'Action, work order ID, and private key are required'})
        
        # Create client
        client = CraftLoreClient(base_url=REST_API_URL, private_key=private_key)
        
        if action == 'accept':
            batch_uid = data.get('batch_uid')
            result = client.accept_work_order(work_order_id, batch_uid)
        elif action == 'reject':
            rejection_reason = data.get('rejection_reason')
            if not rejection_reason:
                return jsonify({'error': 'Rejection reason is required'})
            result = client.reject_work_order(work_order_id, rejection_reason)
        elif action == 'complete':
            units_produced = data.get('units_produced')
            if units_produced is None:
                return jsonify({'error': 'Units produced is required'})
            produced_quantity = data.get('produced_quantity')
            products_price = data.get('products_price')
            result = client.complete_work_order(work_order_id, units_produced, produced_quantity, products_price)
        else:
            return jsonify({'error': f'Invalid action: {action}'})
        
        if result.get('status') == 'success':
            response_data = {
                'success': True,
                'message': f'Work order {action}ed successfully!',
                'batch_link': result.get('link')
            }
            # Include the batch UID for accept action
            if action == 'accept' and result.get('uid'):
                response_data['batch_uid'] = result.get('uid')
            return jsonify(response_data)
        else:
            return jsonify({'error': f"Failed to {action} work order: {result.get('message', result.get('error', 'Unknown error'))}"})
    
    except Exception as e:
        return jsonify({'error': f'Error processing work order action: {str(e)}'})

@app.route('/api/client/add_raw_material_to_batch', methods=['POST'])
def client_add_raw_material_to_batch():
    """Add raw material to a batch."""
    try:
        data = request.json
        batch = data.get('batch')
        raw_material = data.get('raw_material')
        usage_quantity = data.get('usage_quantity')
        private_key = data.get('private_key')
        
        if not all([batch, raw_material, usage_quantity, private_key]):
            return jsonify({'error': 'Batch, raw material, usage quantity, and private key are required'})
        
        # Create client
        client = CraftLoreClient(base_url=REST_API_URL, private_key=private_key)
        
        # Add raw material to batch
        result = client.add_raw_material_to_batch(batch, raw_material, float(usage_quantity))
        
        if result.get('status') == 'success':
            return jsonify({
                'success': True,
                'message': 'Raw material added to batch successfully!',
                'batch_link': result.get('link')
            })
        else:
            return jsonify({'error': f"Failed to add raw material to batch: {result.get('message', result.get('error', 'Unknown error'))}"})
    
    except Exception as e:
        return jsonify({'error': f'Error adding raw material to batch: {str(e)}'})

@app.route('/api/client/complete_batch', methods=['POST'])
def client_complete_batch():
    """Complete a batch."""
    try:
        data = request.json
        batch_id = data.get('batch_id')
        units_produced = data.get('units_produced')
        products_price = data.get('products_price')
        private_key = data.get('private_key')
        produced_quantity = data.get('produced_quantity')
        
        if not all([batch_id, units_produced, products_price, private_key]):
            return jsonify({'error': 'Batch ID, units produced, products price, and private key are required'})
        
        # Create client
        client = CraftLoreClient(base_url=REST_API_URL, private_key=private_key)
        
        # Complete batch
        result = client.complete_batch(batch_id, int(units_produced), float(products_price), 
                                     float(produced_quantity) if produced_quantity else None)
        
        if result.get('status') == 'success':
            return jsonify({
                'success': True,
                'message': 'Batch completed successfully!',
                'batch_link': result.get('link')
            })
        else:
            return jsonify({'error': f"Failed to complete batch: {result.get('message', result.get('error', 'Unknown error'))}"})
    
    except Exception as e:
        return jsonify({'error': f'Error completing batch: {str(e)}'})

@app.route('/api/client/sub_assignment_action', methods=['POST'])
def client_sub_assignment_action():
    """Handle sub assignment actions (accept, reject)."""
    try:
        data = request.json
        action = data.get('action')
        subassignment = data.get('subassignment')
        private_key = data.get('private_key')
        
        if not all([action, subassignment, private_key]):
            return jsonify({'error': 'Action, subassignment ID, and private key are required'})
        
        # Create client
        client = CraftLoreClient(base_url=REST_API_URL, private_key=private_key)
        
        if action == 'accept':
            result = client.accept_sub_assignment(subassignment)
        elif action == 'reject':
            rejection_reason = data.get('rejection_reason')
            if not rejection_reason:
                return jsonify({'error': 'Rejection reason is required'})
            result = client.reject_sub_assignment(subassignment, rejection_reason)
        else:
            return jsonify({'error': f'Invalid action: {action}'})
        
        if result.get('status') == 'success':
            return jsonify({
                'success': True,
                'message': f'Sub assignment {action}ed successfully!',
                'batch_link': result.get('link')
            })
        else:
            return jsonify({'error': f"Failed to {action} sub assignment: {result.get('message', result.get('error', 'Unknown error'))}"})
    
    except Exception as e:
        return jsonify({'error': f'Error processing sub assignment action: {str(e)}'})

@app.route('/api/client/delete_asset', methods=['POST'])
def client_delete_asset():
    """Delete an asset."""
    try:
        data = request.json
        uid = data.get('uid')
        deletion_reason = data.get('deletion_reason')
        private_key = data.get('private_key')
        
        if not all([uid, deletion_reason, private_key]):
            return jsonify({'error': 'Asset UID, deletion reason, and private key are required'})
        
        # Create client
        client = CraftLoreClient(base_url=REST_API_URL, private_key=private_key)
        
        # Delete asset
        result = client.delete_asset(uid, deletion_reason)
        
        if result.get('status') == 'success':
            return jsonify({
                'success': True,
                'message': 'Asset deleted successfully!',
                'batch_link': result.get('link')
            })
        else:
            return jsonify({'error': f"Failed to delete asset: {result.get('message', result.get('error', 'Unknown error'))}"})
    
    except Exception as e:
        return jsonify({'error': f'Error deleting asset: {str(e)}'})

@app.route('/api/client/delete_account', methods=['POST'])
def client_delete_account():
    """Delete an account."""
    try:
        data = request.json
        public_key = data.get('public_key')
        deletion_reason = data.get('deletion_reason')
        private_key = data.get('private_key')
        
        if not all([public_key, deletion_reason, private_key]):
            return jsonify({'error': 'Public key, deletion reason, and private key are required'})
        
        # Create client
        client = CraftLoreClient(base_url=REST_API_URL, private_key=private_key)
        
        # Delete account
        result = client.delete_account(public_key, deletion_reason)
        
        if result.get('status') == 'success':
            return jsonify({
                'success': True,
                'message': 'Account deleted successfully!',
                'batch_link': result.get('link')
            })
        else:
            return jsonify({'error': f"Failed to delete account: {result.get('message', result.get('error', 'Unknown error'))}"})
    
    except Exception as e:
        return jsonify({'error': f'Error deleting account: {str(e)}'})

@app.route('/api/client/edit_asset', methods=['POST'])
def client_edit_asset():
    """Edit an asset."""
    try:
        data = request.json
        uid = data.get('uid')
        updates = data.get('updates')
        private_key = data.get('private_key')
        
        if not all([uid, updates, private_key]):
            return jsonify({'error': 'Asset UID, updates, and private key are required'})
        
        # Create client
        client = CraftLoreClient(base_url=REST_API_URL, private_key=private_key)
        
        # Edit asset
        result = client.edit_asset(uid, updates)
        
        if result.get('status') == 'success':
            return jsonify({
                'success': True,
                'message': 'Asset edited successfully!',
                'batch_link': result.get('link')
            })
        else:
            return jsonify({'error': f"Failed to edit asset: {result.get('message', result.get('error', 'Unknown error'))}"})
    
    except Exception as e:
        return jsonify({'error': f'Error editing asset: {str(e)}'})

@app.route('/api/client/edit_account', methods=['POST'])
def client_edit_account():
    """Edit an account."""
    try:
        data = request.json
        public_key = data.get('public_key')
        updates = data.get('updates')
        private_key = data.get('private_key')
        
        if not all([public_key, updates, private_key]):
            return jsonify({'error': 'Public key, updates, and private key are required'})
        
        # Create client
        client = CraftLoreClient(base_url=REST_API_URL, private_key=private_key)
        
        # Edit account
        result = client.edit_account(public_key, updates)
        
        if result.get('status') == 'success':
            return jsonify({
                'success': True,
                'message': 'Account edited successfully!',
                'batch_link': result.get('link')
            })
        else:
            return jsonify({'error': f"Failed to edit account: {result.get('message', result.get('error', 'Unknown error'))}"})
    
    except Exception as e:
        return jsonify({'error': f'Error editing account: {str(e)}'})

@app.route('/api/client/unpack_product', methods=['POST'])
def client_unpack_product():
    """Unpack a product."""
    try:
        data = request.json
        product_id = data.get('product_id')
        private_key = data.get('private_key')
        
        if not all([product_id, private_key]):
            return jsonify({'error': 'Product ID and private key are required'})
        
        # Create client
        client = CraftLoreClient(base_url=REST_API_URL, private_key=private_key)
        
        # Unpack product
        result = client.unpack_product(product_id)
        
        if result.get('status') == 'success':
            return jsonify({
                'success': True,
                'message': 'Product unpacked successfully!',
                'batch_link': result.get('link')
            })
        else:
            return jsonify({'error': f"Failed to unpack product: {result.get('message', result.get('error', 'Unknown error'))}"})
    
    except Exception as e:
        return jsonify({'error': f'Error unpacking product: {str(e)}'})

@app.route('/api/client/bootstrap', methods=['POST'])
def client_bootstrap():
    """Bootstrap the system."""
    try:
        data = request.json
        email = data.get('email')
        private_key = data.get('private_key')
        
        if not all([email, private_key]):
            return jsonify({'error': 'Email and private key are required'})
        
        # Create client
        client = CraftLoreClient(base_url=REST_API_URL, private_key=private_key)
        
        # Bootstrap
        result = client.bootstrap(email)
        
        if result.get('status') == 'success':
            return jsonify({
                'success': True,
                'message': 'System bootstrapped successfully!',
                'batch_link': result.get('link')
            })
        else:
            return jsonify({'error': f"Failed to bootstrap system: {result.get('message', result.get('error', 'Unknown error'))}"})
    
    except Exception as e:
        return jsonify({'error': f'Error bootstrapping system: {str(e)}'})

@app.route('/api/client/create_admin', methods=['POST'])
def client_create_admin():
    """Create an admin account."""
    try:
        data = request.json
        admin_public_key = data.get('admin_public_key')
        email = data.get('email')
        permission_level = data.get('permission_level')
        action_details = data.get('action_details')
        private_key = data.get('private_key')
        
        if not all([admin_public_key, email, permission_level, action_details, private_key]):
            return jsonify({'error': 'Admin public key, email, permission level, action details, and private key are required'})
        
        # Create client
        client = CraftLoreClient(base_url=REST_API_URL, private_key=private_key)
        
        # Additional fields
        additional_fields = {k: v for k, v in data.items() if k not in ['admin_public_key', 'email', 'permission_level', 'action_details', 'private_key']}
        
        # Create admin
        result = client.create_admin(admin_public_key, email, permission_level, action_details, **additional_fields)
        
        if result.get('status') == 'success':
            return jsonify({
                'success': True,
                'message': 'Admin account created successfully!',
                'batch_link': result.get('link')
            })
        else:
            return jsonify({'error': f"Failed to create admin account: {result.get('message', result.get('error', 'Unknown error'))}"})
    
    except Exception as e:
        return jsonify({'error': f'Error creating admin account: {str(e)}'})

@app.route('/api/client/issue_certification', methods=['POST'])
def client_issue_certification():
    """Issue a certification."""
    try:
        data = request.json
        action_details = data.get('action_details')
        private_key = data.get('private_key')
        
        if not all([action_details, private_key]):
            return jsonify({'error': 'Action details and private key are required'})
        
        # Create client
        client = CraftLoreClient(base_url=REST_API_URL, private_key=private_key)
        
        # Additional fields
        additional_fields = {k: v for k, v in data.items() if k not in ['action_details', 'private_key']}
        
        # Issue certification
        result = client.issue_certification(action_details, **additional_fields)
        
        if result.get('status') == 'success':
            return jsonify({
                'success': True,
                'message': 'Certification issued successfully!',
                'certification_id': result.get('uid'),
                'batch_link': result.get('link')
            })
        else:
            return jsonify({'error': f"Failed to issue certification: {result.get('message', result.get('error', 'Unknown error'))}"})
    
    except Exception as e:
        return jsonify({'error': f'Error issuing certification: {str(e)}'})

@app.route('/api/client/moderator_edit', methods=['POST'])
def client_moderator_edit():
    """Perform moderator edits."""
    try:
        data = request.json
        action_details = data.get('action_details')
        edits = data.get('edits')
        private_key = data.get('private_key')
        
        if not all([action_details, edits, private_key]):
            return jsonify({'error': 'Action details, edits, and private key are required'})
        
        # Create client
        client = CraftLoreClient(base_url=REST_API_URL, private_key=private_key)
        
        # Perform moderator edit
        result = client.moderator_edit(action_details, edits)
        
        if result.get('status') == 'success':
            return jsonify({
                'success': True,
                'message': 'Moderator edits applied successfully!',
                'batch_link': result.get('link')
            })
        else:
            return jsonify({'error': f"Failed to apply moderator edits: {result.get('message', result.get('error', 'Unknown error'))}"})
    
    except Exception as e:
        return jsonify({'error': f'Error applying moderator edits: {str(e)}'})

@app.route('/api/client/authenticate_entity', methods=['POST'])
def client_authenticate_entity():
    """Authenticate an entity (account or asset)."""
    try:
        data = request.json
        entity_type = data.get('entity_type')  # 'account' or 'asset'
        authentication_status = data.get('authentication_status')
        action_details = data.get('action_details')
        private_key = data.get('private_key')
        
        if not all([entity_type, authentication_status, action_details, private_key]):
            return jsonify({'error': 'Entity type, authentication status, action details, and private key are required'})
        
        # Create client
        client = CraftLoreClient(base_url=REST_API_URL, private_key=private_key)
        
        if entity_type == 'account':
            public_key = data.get('public_key')
            if not public_key:
                return jsonify({'error': 'Public key is required for account authentication'})
            result = client.authenticate_account(public_key, authentication_status, action_details)
        elif entity_type == 'asset':
            uid = data.get('uid')
            if not uid:
                return jsonify({'error': 'Asset UID is required for asset authentication'})
            result = client.authenticate_asset(uid, authentication_status, action_details)
        else:
            return jsonify({'error': 'Invalid entity type. Must be "account" or "asset"'})
        
        if result.get('status') == 'success':
            return jsonify({
                'success': True,
                'message': f'{entity_type.capitalize()} authenticated successfully!',
                'batch_link': result.get('link')
            })
        else:
            return jsonify({'error': f"Failed to authenticate {entity_type}: {result.get('message', result.get('error', 'Unknown error'))}"})
    
    except Exception as e:
        return jsonify({'error': f'Error authenticating entity: {str(e)}'})

@app.route('/api/status')
def api_status():
    """Check REST API status."""
    try:
        resp = requests.get(f"{REST_API_URL}/status", timeout=5)
        if resp.status_code == 200:
            return jsonify({'status': 'online', 'data': resp.json()})
        else:
            return jsonify({'status': 'error', 'code': resp.status_code})
    except Exception as e:
        return jsonify({'status': 'offline', 'error': str(e)})

# =============================================
# UTILITY ENDPOINTS
# =============================================

@app.route('/api/enums')
def get_enums():
    """Get available enums for dropdowns."""
    return jsonify({
        'account_types': [e.value for e in AccountType],
        'asset_types': [e.value for e in AssetType],
        'event_types': [e.value for e in EventType],
        'artisan_skill_levels': [e.value for e in ArtisanSkillLevel],
        'admin_permission_levels': [e.value for e in AdminPermissionLevel],
        'work_order_types': [e.value for e in WorkOrderType]
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)