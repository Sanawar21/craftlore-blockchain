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
    email = "baap1.com"
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
    email = "chacha1.com"
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
        package_height=20.0
    )
    print(f"   Result: {result.get('status', 'unknown')}")
    print(f"   Message: {result.get('message', '')}")

if __name__ == "__main__":
    main()
