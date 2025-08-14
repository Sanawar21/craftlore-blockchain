#!/usr/bin/env python3
"""
Asset Operations Client for CraftLore Asset TP.
Handles asset transfers, locking, updates, warranties, and certifications.
"""

import sys
import json
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from base_client import AssetClient


class AssetOperationsClient(AssetClient):
    """Client for asset operations and lifecycle management."""
    
    def transfer_asset(self, asset_id: str, asset_type: str, new_owner: str, 
                      reason: str = None) -> Dict:
        """Transfer asset to new owner."""
        data = {
            'asset_id': asset_id,
            'asset_type': asset_type,
            'new_owner': new_owner,
            'reason': reason or f"Transfer to {new_owner[:16]}...",
            'timestamp': datetime.utcnow().isoformat()
        }
        
        print(f"🔄 Transferring {asset_id} to {new_owner[:16]}...")
        result = self.submit_transaction('transfer_asset', data)
        
        if result.get('status') == 'committed':
            print(f"✅ Asset transferred successfully")
            asset = self.get_asset(asset_id, asset_type)
            if asset:
                print(f"New owner: {asset.get('owner', 'Unknown')[:16]}...")
        else:
            print(f"❌ Transfer failed: {result}")
        
        return result
    
    def bulk_transfer(self, asset_list: List[Dict], new_owner: str) -> Dict:
        """Transfer multiple assets to new owner."""
        data = {
            'asset_ids': asset_list,  # List of {'asset_id': id, 'asset_type': type}
            'new_owner': new_owner,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        print(f"📦 Bulk transferring {len(asset_list)} assets to {new_owner[:16]}...")
        result = self.submit_transaction('bulk_transfer', data)
        
        if result.get('status') == 'committed':
            print(f"✅ Bulk transfer completed")
            # Show transfer results if available
            if isinstance(result, dict) and 'transferred_assets' in result:
                print(f"Transferred: {len(result.get('transferred_assets', []))}")
                print(f"Failed: {len(result.get('failed_transfers', []))}")
        else:
            print(f"❌ Bulk transfer failed: {result}")
        
        return result
    
    def lock_asset(self, asset_id: str, asset_type: str, reason: str = None) -> Dict:
        """Lock asset to prevent modifications."""
        data = {
            'asset_id': asset_id,
            'asset_type': asset_type,
            'reason': reason or "Locked for processing",
            'timestamp': datetime.utcnow().isoformat()
        }
        
        print(f"🔒 Locking asset: {asset_id}")
        result = self.submit_transaction('lock_asset', data)
        
        if result.get('status') == 'committed':
            print(f"✅ Asset locked successfully")
            asset = self.get_asset(asset_id, asset_type)
            if asset:
                print(f"Lock reason: {asset.get('lock_reason', 'Unknown')}")
        else:
            print(f"❌ Lock failed: {result}")
        
        return result
    
    def unlock_asset(self, asset_id: str, asset_type: str) -> Dict:
        """Unlock asset to allow modifications."""
        data = {
            'asset_id': asset_id,
            'asset_type': asset_type,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        print(f"🔓 Unlocking asset: {asset_id}")
        result = self.submit_transaction('unlock_asset', data)
        
        if result.get('status') == 'committed':
            print(f"✅ Asset unlocked successfully")
        else:
            print(f"❌ Unlock failed: {result}")
        
        return result
    
    def update_asset(self, asset_id: str, asset_type: str, updates: Dict) -> Dict:
        """Update asset with new data."""
        data = {
            'asset_id': asset_id,
            'asset_type': asset_type,
            'updates': updates,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        print(f"✏️  Updating asset: {asset_id}")
        print(f"Updates: {updates}")
        result = self.submit_transaction('update_asset', data)
        
        if result.get('status') == 'committed':
            print(f"✅ Asset updated successfully")
            asset = self.get_asset(asset_id, asset_type)
            if asset:
                print(f"Updated fields applied")
        else:
            print(f"❌ Update failed: {result}")
        
        return result
    
    def delete_asset(self, asset_id: str, asset_type: str, reason: str = None) -> Dict:
        """Soft delete asset."""
        data = {
            'asset_id': asset_id,
            'asset_type': asset_type,
            'reason': reason or "Deleted by owner",
            'timestamp': datetime.utcnow().isoformat()
        }
        
        print(f"🗑️  Deleting asset: {asset_id}")
        result = self.submit_transaction('delete_asset', data)
        
        if result.get('status') == 'committed':
            print(f"✅ Asset deleted successfully")
        else:
            print(f"❌ Delete failed: {result}")
        
        return result
    
    def accept_asset(self, asset_id: str, asset_type: str) -> Dict:
        """Accept work order and transfer associated product batch (Flow 1)."""
        # Only work orders can be accepted
        if asset_type != 'work_order':
            print(f"❌ Error: Only work orders can be accepted, not {asset_type}")
            return {'status': 'error', 'message': 'Only work orders can be accepted'}
        
        data = {
            'asset_id': asset_id,
            'asset_type': asset_type,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        print(f"✅ Accepting work order: {asset_id}")
        result = self.submit_transaction('accept_asset', data)
        
        if result.get('status') == 'committed':
            print(f"✅ Work order accepted successfully")
            if result.get('batch_transferred'):
                print(f"✅ Product batch transferred to assignee: {result.get('new_batch_owner', 'Unknown')[:16]}...")
            work_order = self.get_asset(asset_id, asset_type)
            if work_order:
                print(f"Work order status: {work_order.get('status', 'Unknown')}")
        else:
            print(f"❌ Accept failed: {result}")
        
        return result
    
    def register_warranty(self, asset_id: str, asset_type: str, warranty_data: Dict) -> Dict:
        """Register or update warranty for an asset."""
        data = {
            'asset_id': asset_id,
            'asset_type': asset_type,
            'warranty_data': warranty_data,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        print(f"🛡️  Registering warranty for: {asset_id}")
        result = self.submit_transaction('register_warranty', data)
        
        if result.get('status') == 'committed':
            print(f"✅ Warranty registered successfully")
            asset = self.get_asset(asset_id, asset_type)
            if asset:
                print(f"Warranty ID: {asset.get('warranty_id', 'Unknown')}")
        else:
            print(f"❌ Warranty registration failed: {result}")
        
        return result
    
    def update_certification(self, asset_id: str, asset_type: str, 
                           certification_data: Dict) -> Dict:
        """Update certification status or information for an asset."""
        data = {
            'asset_id': asset_id,
            'asset_type': asset_type,
            'certification_data': certification_data,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        print(f"📜 Updating certification for: {asset_id}")
        result = self.submit_transaction('update_certification', data)
        
        if result.get('status') == 'committed':
            print(f"✅ Certification updated successfully")
        else:
            print(f"❌ Certification update failed: {result}")
        
        return result
    
    def update_sustainability(self, asset_id: str, asset_type: str, 
                            sustainability_data: Dict) -> Dict:
        """Update sustainability metrics and certifications."""
        data = {
            'asset_id': asset_id,
            'asset_type': asset_type,
            'sustainability_data': sustainability_data,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        print(f"🌱 Updating sustainability data for: {asset_id}")
        result = self.submit_transaction('update_sustainability', data)
        
        if result.get('status') == 'committed':
            print(f"✅ Sustainability data updated successfully")
        else:
            print(f"❌ Sustainability update failed: {result}")
        
        return result


def main():
    """Main CLI for asset operations."""
    if len(sys.argv) < 2:
        print("Usage: python asset_operations_client.py <command> [args...]")
        print("\nCommands:")
        print("  transfer <asset_id> <asset_type> <new_owner> [reason]")
        print("  bulk_transfer <new_owner> <asset1_id:type> <asset2_id:type> ...")
        print("  lock <asset_id> <asset_type> [reason]")
        print("  unlock <asset_id> <asset_type>")
        print("  update <asset_id> <asset_type> <field>=<value> ...")
        print("  delete <asset_id> <asset_type> [reason]")
        print("  accept <work_order_id> work_order  # Only work orders can be accepted")
        print("  warranty <asset_id> <asset_type> <provider> <type> <start_date> <end_date>")
        print("  certify <asset_id> <asset_type> <cert_type> <authority> <issue_date>")
        print("  sustainability <asset_id> <asset_type> <metric>=<value> ...")
        print("  demo - Run operations demo")
        return
    
    client = AssetOperationsClient()
    command = sys.argv[1]
    
    try:
        if command == "transfer" and len(sys.argv) >= 5:
            reason = sys.argv[5] if len(sys.argv) > 5 else None
            client.transfer_asset(sys.argv[2], sys.argv[3], sys.argv[4], reason)
        
        elif command == "bulk_transfer" and len(sys.argv) >= 4:
            new_owner = sys.argv[2]
            asset_list = []
            for arg in sys.argv[3:]:
                if ':' in arg:
                    asset_id, asset_type = arg.split(':', 1)
                    asset_list.append({'asset_id': asset_id, 'asset_type': asset_type})
            client.bulk_transfer(asset_list, new_owner)
        
        elif command == "lock" and len(sys.argv) >= 4:
            reason = sys.argv[4] if len(sys.argv) > 4 else None
            client.lock_asset(sys.argv[2], sys.argv[3], reason)
        
        elif command == "unlock" and len(sys.argv) >= 4:
            client.unlock_asset(sys.argv[2], sys.argv[3])
        
        elif command == "update" and len(sys.argv) >= 5:
            updates = {}
            for arg in sys.argv[4:]:
                if '=' in arg:
                    key, value = arg.split('=', 1)
                    # Try to parse as JSON, fall back to string
                    try:
                        updates[key] = json.loads(value)
                    except:
                        updates[key] = value
            client.update_asset(sys.argv[2], sys.argv[3], updates)
        
        elif command == "delete" and len(sys.argv) >= 4:
            reason = sys.argv[4] if len(sys.argv) > 4 else None
            client.delete_asset(sys.argv[2], sys.argv[3], reason)
        
        elif command == "accept" and len(sys.argv) >= 4:
            client.accept_asset(sys.argv[2], sys.argv[3])
        
        elif command == "warranty" and len(sys.argv) >= 8:
            warranty_data = {
                'warranty_provider': sys.argv[4],
                'warranty_type': sys.argv[5],
                'start_date': sys.argv[6],
                'end_date': sys.argv[7],
                'terms': 'Standard warranty terms apply'
            }
            client.register_warranty(sys.argv[2], sys.argv[3], warranty_data)
        
        elif command == "certify" and len(sys.argv) >= 7:
            cert_data = {
                'operation': 'add',
                'certification_type': sys.argv[4],
                'certifying_authority': sys.argv[5],
                'issue_date': sys.argv[6],
                'certificate_number': f"CERT-{sys.argv[2]}-{datetime.now().strftime('%Y%m%d')}"
            }
            client.update_certification(sys.argv[2], sys.argv[3], cert_data)
        
        elif command == "sustainability" and len(sys.argv) >= 5:
            sustainability_data = {}
            for arg in sys.argv[4:]:
                if '=' in arg:
                    key, value = arg.split('=', 1)
                    try:
                        sustainability_data[key] = float(value)
                    except:
                        sustainability_data[key] = value
            client.update_sustainability(sys.argv[2], sys.argv[3], sustainability_data)
        
        elif command == "demo":
            run_operations_demo(client)
        
        else:
            print("Invalid command or missing arguments")
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


def run_operations_demo(client: AssetOperationsClient):
    """Run a demonstration of asset operations."""
    print("🎯 Starting Asset Operations Demo")
    print("=" * 50)
    
    # Assume we have some assets created (you might need to run creation demo first)
    demo_assets = [
        ('PRODUCT_KANI_001', 'product'),
        ('BATCH_KANI_SHAWL_001', 'product_batch'),
        ('WO_KANI_001', 'work_order')
    ]
    
    print("\n1️⃣  Locking Assets...")
    for asset_id, asset_type in demo_assets:
        client.lock_asset(asset_id, asset_type, "Demo lock for testing")
    
    print("\n2️⃣  Updating Asset Information...")
    client.update_asset('PRODUCT_KANI_001', 'product', {
        'current_price': 299.99,
        'description': 'Premium hand-woven Kani pashmina shawl'
    })
    
    print("\n3️⃣  Registering Warranty...")
    warranty_data = {
        'warranty_provider': 'CraftLore Warranty Services',
        'warranty_type': 'manufacturing_defects',
        'start_date': datetime.now().strftime('%Y-%m-%d'),
        'end_date': (datetime.now() + timedelta(days=730)).strftime('%Y-%m-%d'),
        'terms': 'Covers manufacturing defects for 2 years',
        'contact_info': 'warranty@craftlore.com'
    }
    client.register_warranty('PRODUCT_KANI_001', 'product', warranty_data)
    
    print("\n4️⃣  Adding Certifications...")
    cert_data = {
        'operation': 'add',
        'certification_type': 'GI_Kashmir',
        'certifying_authority': 'Kashmir Handicrafts Board',
        'issue_date': datetime.now().strftime('%Y-%m-%d'),
        'certificate_number': 'GI-KAS-2024-001',
        'verification_url': 'https://verify.kashmir.gov.in/GI-KAS-2024-001'
    }
    client.update_certification('PRODUCT_KANI_001', 'product', cert_data)
    
    print("\n5️⃣  Updating Sustainability Metrics...")
    sustainability_data = {
        'carbon_footprint': 2.5,  # kg CO2
        'water_usage': 150.0,     # liters
        'renewable_energy_used': 85.0,  # percentage
        'waste_generated': 0.2    # kg
    }
    client.update_sustainability('PRODUCT_KANI_001', 'product', sustainability_data)
    
    print("\n6️⃣  Accepting Work Order...")
    # Demonstrate work order acceptance (Flow 1)
    client.accept_asset('WO_KANI_001', 'work_order')
    
    print("\n7️⃣  Unlocking Assets...")
    for asset_id, asset_type in demo_assets:
        if asset_type != 'work_order':  # Skip work order since it's now accepted
            client.unlock_asset(asset_id, asset_type)
    
    print("\n8️⃣  Transferring Asset...")
    # Create a new key for demo transfer
    new_owner = client.public_key  # In real scenario, this would be different
    client.transfer_asset('PRODUCT_KANI_001', 'product', new_owner, 
                         "Demo transfer to new owner")
    
    print("\n🎉 Operations demo completed!")
    print("=" * 50)


if __name__ == "__main__":
    main()
