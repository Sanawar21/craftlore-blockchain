from .craftlore_client import CraftLoreClient
from models.enums import AccountType, AssetType, ArtisanSkillLevel
import time

def main():
    """Interactive CLI for the client."""
    baap = CraftLoreClient()
    chacha = CraftLoreClient()

    print("=" * 60)
    print("CraftLore Combined TP Client")
    print("=" * 60)
    

    print("1. Create Account for baap")
    account_type = AccountType.ARTISAN
    email = "ba11p21121.com"
    result = baap.create_account(
        account_type, 
        email,
        skill_level=ArtisanSkillLevel.EXPERT,
        years_of_experience=10)
    print(f"   Result: {result.get('status', 'unknown')}")
    print(f"   Message: {result.get('message', '')}")
    time.sleep(1)

    print("2. Create Account for chacha")
    account_type = AccountType.SUPPLIER
    email = "chac1h1a21121.com"
    result = chacha.create_account(account_type, email)
    print(f"   Result: {result.get('status', 'unknown')}")
    print(f"   Message: {result.get('message', '')}")
    time.sleep(1)
            
            
    print("\n2. Create Work Order Asset by chacha")
    asset_type = AssetType.WORK_ORDER
    result = chacha.create_asset(
        asset_type,
        assignee=baap.public_key,
        product_description="This is a work order from chacha to baap",
        requested_quantity=10,
        requested_quantity_unit="pieces",
        total_price_usd=1500.0,
    )
    print(f"   Result: {result.get('status', 'unknown')}")
    print(f"   Message: {result.get('message', '')}")
    time.sleep(1)

    print("\n3. Accept Work Order by baap")
    work_order_id = result.get("uid")
    if not work_order_id:
        print("   Error: Work order ID not found, cannot accept work order.")
        return
    result = baap.accept_work_order(work_order_id)
    batch_uid = result.get("uid")
    print(f"   Result: {result.get('status', 'unknown')}")
    print(f"   Message: {result.get('message', '')}")
    time.sleep(1)
    
    print("\n4. Complete Work Order by baap")
    result = baap.complete_work_order(work_order_id, units_produced=10)
    print(f"   Result: {result.get('status', 'unknown')}")
    print(f"   Message: {result.get('message', '')}")

    time.sleep(1)
    print("\n5. Create Packaging by baap")
    result = baap.create_asset(
        AssetType.PACKAGING,
        products=[f"{batch_uid}-{i}" for i in range(1,11)],
        package_type="Box",
        materials_used=["Cardboard", "Tape"],
        labelling={"label": "Fragile"},
        seal_id="SEAL12345",
        net_weight=5.0,
        gross_weight=5.5,
        package_width=30.0,
        package_height=20.0,
        price_usd=200.0
    )
    print(f"   Result: {result.get('status', 'unknown')}")
    print(f"   Message: {result.get('message', '')}")
    package_uid = result["uid"]

    time.sleep(1)
    print("\n6. Transfer Package from baap to chacha")
    result = baap.transfer_assets(
        [package_uid],
        recipient=chacha.public_key,
        logistics={            
            "carrier": "DHL",
            "tracking_id": "DHL123456789",
            "origin": "Supplier Warehouse, City A",
            "destination": "Artisan Workshop, City B",
            "dispatch_date": baap.serializer.get_current_timestamp(),
            "estimated_delivery_date": baap.serializer.get_current_timestamp(),
            "freight_cost_usd": 50.0
        }
    )
    print(f"   Result: {result.get('status', 'unknown')}")
    print(f"   Message: {result.get('message', '')}")
    time.sleep(1)

    print("7. unpack a product ")
    result = chacha.unpack_product(f"{batch_uid}-1")
    print(f"   Result: {result.get('status', 'unknown')}")
    print(f"   Message: {result.get('message', '')}")

    time.sleep(1)

    print("\n8. Transfer unpacked product from chacha to baap")
    result = chacha.transfer_assets(
        [f"{batch_uid}-1"],
        recipient=baap.public_key,
        logistics={            
            "carrier": "FedEx",
            "tracking_id": "FedEx987654321",
            "origin": "Artisan Workshop, City B",
            "destination": "Supplier Warehouse, City A",
            "dispatch_date": chacha.serializer.get_current_timestamp(),
            "estimated_delivery_date": chacha.serializer.get_current_timestamp(),
            "freight_cost_usd": 30.0
        }
        )
    print(f"   Result: {result.get('status', 'unknown')}")
    print(f"   Message: {result.get('message', '')}")
    time.sleep(1)

    print("\n9. Transfer packed product from chacha to baap")
    result = chacha.transfer_assets(
        [f"{batch_uid}-2"],
        recipient=baap.public_key,
        logistics={
            "carrier": "FedEx",
            "tracking_id": "FedEx987654322",
            "origin": "Artisan Workshop, City B",
            "destination": "Supplier Warehouse, City A",
            "dispatch_date": chacha.serializer.get_current_timestamp(),
            "estimated_delivery_date": chacha.serializer.get_current_timestamp(),
            "freight_cost_usd": 30.0
        }
        )
    print(f"   Result: {result.get('status', 'unknown')}")
    print(f"   Message: {result.get('message', '')}")

    print("\n9. Transfer packed product with packaging from chacha to baap")
    result = chacha.transfer_assets(
        [f"{batch_uid}-2", package_uid],
        recipient=baap.public_key,
        logistics={
            "carrier": "FedEx",
            "tracking_id": "FedEx987654322",
            "origin": "Artisan Workshop, City B",
            "destination": "Supplier Warehouse, City A",
            "dispatch_date": chacha.serializer.get_current_timestamp(),
            "estimated_delivery_date": chacha.serializer.get_current_timestamp(),
            "freight_cost_usd": 30.0
        }
        )
    print(f"   Result: {result.get('status', 'unknown')}")
    print(f"   Message: {result.get('message', '')}")


if __name__ == "__main__":
    main()
