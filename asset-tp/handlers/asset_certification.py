#!/usr/bin/env python3
"""
Asset certification and warranty operations for CraftLore Asset TP.
"""

from typing import Dict
from datetime import datetime
from sawtooth_sdk.processor.context import Context
from sawtooth_sdk.processor.exceptions import InvalidTransaction
from core.enums import AssetStatus, AssetType, CertificationStatus, WarrantyStatus
from entities import AssetFactory
from .asset_utils import AssetUtils


class AssetCertificationHandler:
    """Handler for asset certification and warranty operations."""
    
    def __init__(self, address_generator, serializer):
        self.asset_utils = AssetUtils(address_generator, serializer)
    
    def register_warranty(self, context: Context, transaction_data: Dict) -> Dict:
        """Register or update warranty for an asset."""
        try:
            asset_id = transaction_data['asset_id']
            asset_type = transaction_data['asset_type']
            warranty_data = transaction_data['warranty_data']
            signer_public_key = transaction_data.get('signer_public_key')
            timestamp = transaction_data.get('timestamp', datetime.utcnow().isoformat())
            
            # Get current asset
            asset_data = self.asset_utils.get_asset(context, asset_id, asset_type)
            if not asset_data:
                raise InvalidTransaction(f"Asset {asset_id} not found")
            
            # Check permissions - only owner or manufacturer can register warranty
            if not self.asset_utils.can_modify_asset(signer_public_key, asset_data):
                # Check if signer is the manufacturer
                if asset_data.get('manufacturer_id') != signer_public_key:
                    raise InvalidTransaction("Only owner or manufacturer can register warranty")
            
            # Validate warranty data
            required_fields = ['warranty_provider', 'warranty_type', 'start_date', 'end_date']
            for field in required_fields:
                if field not in warranty_data:
                    raise InvalidTransaction(f"Missing required warranty field: {field}")
            
            # Set warranty information
            asset_data['warranty_id'] = warranty_data.get('warranty_id', f"WR-{asset_id}-{timestamp}")
            asset_data['warranty_provider'] = warranty_data['warranty_provider']
            asset_data['warranty_type'] = warranty_data['warranty_type']
            asset_data['warranty_start_date'] = warranty_data['start_date']
            asset_data['warranty_end_date'] = warranty_data['end_date']
            asset_data['warranty_terms'] = warranty_data.get('terms', '')
            asset_data['warranty_status'] = WarrantyStatus.ACTIVE.value
            asset_data['warranty_registered_at'] = timestamp
            asset_data['warranty_registered_by'] = signer_public_key
            
            # Add optional fields
            if 'coverage_details' in warranty_data:
                asset_data['warranty_coverage'] = warranty_data['coverage_details']
            if 'contact_info' in warranty_data:
                asset_data['warranty_contact'] = warranty_data['contact_info']
            
            # Add history entry
            self.asset_utils.add_asset_history(asset_data, {
                'action': 'warranty_registered',
                'warranty_id': asset_data['warranty_id'],
                'warranty_provider': warranty_data['warranty_provider'],
                'warranty_type': warranty_data['warranty_type'],
                'actor': signer_public_key
            }, timestamp)
            
            # Store updated asset
            self.asset_utils.store_asset(context, asset_data)
            
            return {
                'status': 'success',
                'message': f'Warranty registered for asset {asset_id}',
                'warranty_id': asset_data['warranty_id']
            }
            
        except Exception as e:
            raise InvalidTransaction(f"Warranty registration failed: {str(e)}")
    
    def update_certification(self, context: Context, transaction_data: Dict) -> Dict:
        """Update certification status or information for an asset."""
        try:
            asset_id = transaction_data['asset_id']
            asset_type = transaction_data['asset_type']
            certification_data = transaction_data['certification_data']
            signer_public_key = transaction_data.get('signer_public_key')
            timestamp = transaction_data.get('timestamp', datetime.utcnow().isoformat())
            
            # Get current asset
            asset_data = self.asset_utils.get_asset(context, asset_id, asset_type)
            if not asset_data:
                raise InvalidTransaction(f"Asset {asset_id} not found")
            
            # Check permissions - only certifying authority or owner can update
            if not self.asset_utils.can_modify_asset(signer_public_key, asset_data):
                # TODO: Check if signer is authorized certifying authority
                raise InvalidTransaction("Insufficient permissions to update certification")
            
            # Initialize certifications list if not exists
            if 'certifications' not in asset_data:
                asset_data['certifications'] = []
            
            # Handle different certification operations
            operation = certification_data.get('operation', 'add')
            
            if operation == 'add':
                # Add new certification
                required_fields = ['certification_type', 'certifying_authority', 'issue_date']
                for field in required_fields:
                    if field not in certification_data:
                        raise InvalidTransaction(f"Missing required certification field: {field}")
                
                new_cert = {
                    'certification_id': certification_data.get('certification_id', f"CERT-{asset_id}-{len(asset_data['certifications'])}"),
                    'certification_type': certification_data['certification_type'],
                    'certifying_authority': certification_data['certifying_authority'],
                    'issue_date': certification_data['issue_date'],
                    'expiry_date': certification_data.get('expiry_date'),
                    'status': CertificationStatus.VALID.value,
                    'certificate_number': certification_data.get('certificate_number'),
                    'verification_url': certification_data.get('verification_url'),
                    'added_by': signer_public_key,
                    'added_at': timestamp
                }
                
                asset_data['certifications'].append(new_cert)
                
                # Add history entry
                self.asset_utils.add_asset_history(asset_data, {
                    'action': 'certification_added',
                    'certification_type': new_cert['certification_type'],
                    'certifying_authority': new_cert['certifying_authority'],
                    'certification_id': new_cert['certification_id'],
                    'actor': signer_public_key
                }, timestamp)
            
            elif operation == 'update_status':
                # Update existing certification status
                cert_id = certification_data.get('certification_id')
                new_status = certification_data.get('new_status')
                
                if not cert_id or not new_status:
                    raise InvalidTransaction("certification_id and new_status required for status update")
                
                # Find and update certification
                cert_found = False
                for cert in asset_data['certifications']:
                    if cert['certification_id'] == cert_id:
                        old_status = cert['status']
                        cert['status'] = new_status
                        cert['last_updated'] = timestamp
                        cert['updated_by'] = signer_public_key
                        cert_found = True
                        
                        # Add history entry
                        self.asset_utils.add_asset_history(asset_data, {
                            'action': 'certification_status_updated',
                            'certification_id': cert_id,
                            'old_status': old_status,
                            'new_status': new_status,
                            'actor': signer_public_key
                        }, timestamp)
                        break
                
                if not cert_found:
                    raise InvalidTransaction(f"Certification {cert_id} not found")
            
            elif operation == 'revoke':
                # Revoke certification
                cert_id = certification_data.get('certification_id')
                revocation_reason = certification_data.get('reason', 'No reason provided')
                
                if not cert_id:
                    raise InvalidTransaction("certification_id required for revocation")
                
                # Find and revoke certification
                cert_found = False
                for cert in asset_data['certifications']:
                    if cert['certification_id'] == cert_id:
                        cert['status'] = CertificationStatus.REVOKED.value
                        cert['revoked_at'] = timestamp
                        cert['revoked_by'] = signer_public_key
                        cert['revocation_reason'] = revocation_reason
                        cert_found = True
                        
                        # Add history entry
                        self.asset_utils.add_asset_history(asset_data, {
                            'action': 'certification_revoked',
                            'certification_id': cert_id,
                            'reason': revocation_reason,
                            'actor': signer_public_key
                        }, timestamp)
                        break
                
                if not cert_found:
                    raise InvalidTransaction(f"Certification {cert_id} not found")
            
            else:
                raise InvalidTransaction(f"Unknown certification operation: {operation}")
            
            # Store updated asset
            self.asset_utils.store_asset(context, asset_data)
            
            return {
                'status': 'success',
                'message': f'Certification {operation} completed for asset {asset_id}',
                'operation': operation
            }
            
        except Exception as e:
            raise InvalidTransaction(f"Certification update failed: {str(e)}")
    
    def update_sustainability(self, context: Context, transaction_data: Dict) -> Dict:
        """Update sustainability metrics and certifications."""
        try:
            asset_id = transaction_data['asset_id']
            asset_type = transaction_data['asset_type']
            sustainability_data = transaction_data['sustainability_data']
            signer_public_key = transaction_data.get('signer_public_key')
            timestamp = transaction_data.get('timestamp', datetime.utcnow().isoformat())
            
            # Get current asset
            asset_data = self.asset_utils.get_asset(context, asset_id, asset_type)
            if not asset_data:
                raise InvalidTransaction(f"Asset {asset_id} not found")
            
            # Check permissions
            if not self.asset_utils.can_modify_asset(signer_public_key, asset_data):
                raise InvalidTransaction("Insufficient permissions to update sustainability data")
            
            # Initialize sustainability data if not exists
            if 'sustainability_metrics' not in asset_data:
                asset_data['sustainability_metrics'] = {}
            
            # Track changes
            changes = {}
            
            # Update sustainability metrics
            for metric, value in sustainability_data.items():
                if metric in ['carbon_footprint', 'water_usage', 'waste_generated', 'renewable_energy_used']:
                    old_value = asset_data['sustainability_metrics'].get(metric)
                    if old_value != value:
                        asset_data['sustainability_metrics'][metric] = value
                        changes[metric] = {'old': old_value, 'new': value}
                
                elif metric == 'sustainability_certifications':
                    # Handle sustainability certifications
                    if 'sustainability_certifications' not in asset_data:
                        asset_data['sustainability_certifications'] = []
                    
                    for cert in value:
                        # Check if certification already exists
                        exists = any(
                            existing['certification_type'] == cert['certification_type'] 
                            for existing in asset_data['sustainability_certifications']
                        )
                        
                        if not exists:
                            cert['added_at'] = timestamp
                            cert['added_by'] = signer_public_key
                            asset_data['sustainability_certifications'].append(cert)
                            changes[f"sustainability_cert_{cert['certification_type']}"] = {'old': None, 'new': cert}
            
            if not changes:
                return {'status': 'success', 'message': 'No changes made to sustainability data'}
            
            # Update last modified
            asset_data['sustainability_last_updated'] = timestamp
            
            # Add history entry
            self.asset_utils.add_asset_history(asset_data, {
                'action': 'sustainability_updated',
                'changes': changes,
                'actor': signer_public_key
            }, timestamp)
            
            # Store updated asset
            self.asset_utils.store_asset(context, asset_data)
            
            return {
                'status': 'success',
                'message': f'Sustainability data updated for asset {asset_id}',
                'changes': changes
            }
            
        except Exception as e:
            raise InvalidTransaction(f"Sustainability update failed: {str(e)}")
