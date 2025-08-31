import time
import sys
import os
sys.path.append('/app')

from clients.combined_client import CraftLoreClient

# Super admin client (for bootstrapping)
admin_client = CraftLoreClient(base_url='http://rest-api:8008', private_key="ba4817a5951802b29efd2250d62795721b26224975b8a7b3b6b13398f6bd8553")
print(f"Super Admin Public Key: {admin_client.public_key}")

# Buyer client (who will request custom products)
buyer_client = CraftLoreClient(base_url='http://rest-api:8008', private_key="1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef")
print(f"Buyer Public Key: {buyer_client.public_key}")

# Supplier client (provides raw materials)
supplier_client = CraftLoreClient(base_url='http://rest-api:8008', private_key="4888fdf00249c34ce929206d1c51a37e01183ab56721897a939285ad31a6ebbf")
print(f"Supplier Public Key: {supplier_client.public_key}")

# Workshop client (produces the products)
workshop_client = CraftLoreClient(base_url='http://rest-api:8008', private_key="9d2d2ff5837f90a4af442847efa6ba1f5d08630fb348384876fb1266d4e4c517")
print(f"Workshop Public Key: {workshop_client.public_key}")


def create_work_order():
    print("📋 Creating Work Order...")
    result = buyer_client.create_work_order(
        work_order_id='sanawar_batch_2',
        buyer_id=buyer_client.public_key,
        product_batch_id='fresh_batch_003',  # This will be created later by workshop
        assignee_id=workshop_client.public_key,
        description='Custom order for 8 luxury Kashmir shawls with premium materials',
        work_type='production',
        estimated_completion_date='2025-09-15',
        order_quantity=8  # Buyer wants 8 shawls
    )
    print(f"   Result: {result.get('status', 'unknown')}")
    if result.get('status') == 'success':
        print(f"   ✅ Work order created: {result.get('message', 'Order placed successfully')}")
    else:
        print(f"   ❌ Error: {result.get('message', 'Unknown error')}")
    time.sleep(1)

def test_contructor():
    from entities import WorkOrder
    wo = WorkOrder.from_dict(
        dict(
          asset_id='sanawar_batch',
          owner=buyer_client.public_key,
          batch_id='fresh_batch_003',  # This will be created later by workshop
          assigner_id=buyer_client.public_key,
          assignee_id=workshop_client.public_key,
          description='Custom order for 8 luxury Kashmir shawls with premium materials',
          work_type='production',
          estimated_completion_date='2025-09-15',
          order_quantity=8  # Buyer wants 8 shawls
        )
    )

    print(wo.to_dict())


if __name__ == "__main__":
    create_work_order()
    # test_contructor()