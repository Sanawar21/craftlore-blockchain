from .craftlore_client import CraftLoreClient
from models.enums import AccountType, AssetType, ArtisanSkillLevel
import time

def main():
    """Interactive CLI for the client."""
    artisan = CraftLoreClient()
    supplier = CraftLoreClient()
    buyer = CraftLoreClient()

    print("=" * 60)
    print("CraftLore Combined TP Client")
    print("=" * 60)
    
    emails = {
        artisan.public_key: "artisan9.com",
        supplier.public_key: "supplier9.com",
        buyer.public_key: "buyer9.com"
    }

    print("1. Create Account for artisan")
    account_type = AccountType.ARTISAN
    email = emails[artisan.public_key]
    result = artisan.create_account(
        account_type, 
        email,
        skill_level=ArtisanSkillLevel.EXPERT,
        years_of_experience=10)
    print(f"   Result: {result.get('status', 'unknown')}")
    print(f"   Message: {result.get('message', '')}")
    time.sleep(1)

    print("2. Create Account for supplier")
    account_type = AccountType.SUPPLIER
    email = emails[supplier.public_key]
    result = supplier.create_account(account_type, email)
    print(f"   Result: {result.get('status', 'unknown')}")
    print(f"   Message: {result.get('message', '')}")
    time.sleep(1)
            

    print("3. Create Account for buyer")
    account_type = AccountType.BUYER
    email = emails[buyer.public_key]
    result = buyer.create_account(account_type, email)
    print(f"   Result: {result.get('status', 'unknown')}")
    print(f"   Message: {result.get('message', '')}")
    time.sleep(1)
            
    print("\n2. Create Work Order Asset by buyer")
    asset_type = AssetType.WORK_ORDER
    result = buyer.create_asset(
        asset_type,
        assignee=artisan.public_key,
        product_description="This is a work order from buyer to artisan for handcrafted wooden furniture.",
        requested_quantity=10,
        requested_quantity_unit="pieces",
        total_price_usd=1500.0,
    )

    print(f"   Result: {result.get('status', 'unknown')}")
    print(f"   Message: {result.get('message', '')}")
    time.sleep(1)

    print("\n3. Accept Work Order by artisan")
    work_order_id = result.get("uid")
    if not work_order_id:
        print("   Error: Work order ID not found, cannot accept work order.")
        return
    result = artisan.accept_work_order(work_order_id)
    batch_uid = result.get("uid")
    print(f"   Result: {result.get('status', 'unknown')}")
    print(f"   Message: {result.get('message', '')}")
    time.sleep(1)

    print("\n4. Supplier creates Raw Material Asset")
    asset_type = AssetType.RAW_MATERIAL
    result = supplier.create_asset(
        asset_type,
        material_type="Wood",
        quantity=100.0,
        quantity_unit="kg",
        unit_price_usd=5.0,
        harvested_date=supplier.serializer.get_current_timestamp(),
    )
    raw_material_id = result.get("uid")
    print(f"   Result: {result.get('status', 'unknown')}")
    print(f"   Message: {result.get('message', '')}")
    time.sleep(1)


    print("\n5. Transfer Raw Material from supplier to artisan")
    if not raw_material_id:
        print("   Error: Raw material ID not found, cannot transfer raw material.")
        return
    result = supplier.transfer_assets(
        [raw_material_id],
        recipient=artisan.public_key,
        logistics={
            "uid": supplier.serializer.create_asset_id(),
            "carrier": "DHL",
            "tracking_id": "DHL123456789",
            "origin": "Supplier Warehouse, City A",
            "destination": "Artisan Workshop, City B",
            "recipient": artisan.public_key,
            "dispatch_date": supplier.serializer.get_current_timestamp(),
            "estimated_delivery_date": supplier.serializer.get_current_timestamp(),
            "freight_cost_usd": 50.0
        }
    )
    print(f"   Result: {result.get('status', 'unknown')}")
    print(f"   Message: {result.get('message', '')}")
    time.sleep(1)


    print("\n6. Add raw material to batch")
    result = artisan.add_raw_material_to_batch(
        batch=batch_uid,
        raw_material=raw_material_id,
        usage_quantity=20.0
    )
    print(f"   Result: {result.get('status', 'unknown')}")
    print(f"   Message: {result.get('message', '')}")
    time.sleep(1)

if __name__ == "__main__":
    main()
