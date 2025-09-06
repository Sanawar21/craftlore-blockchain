from .craftlore_client import CraftLoreClient, AccountType, EventType, AssetType
import time

def main():
    """Interactive CLI for the client."""
    client = CraftLoreClient()
    
    print("=" * 60)
    print("CraftLore Combined TP Client")
    print("=" * 60)
    

    print("1. Create Account")
    account_type = AccountType.SUPPLIER
    email = "beta.com"
    result = client.create_account(account_type, email)
    print(f"   Result: {result.get('status', 'unknown')}")
    print(f"   Message: {result.get('message', '')}")
    time.sleep(1)
            
    print("\n2. Create Asset")
    asset_type = AssetType.RAW_MATERIAL
    result = client.create_asset(
        asset_type,
        material_type="Wood",
        quantity=100.0,
        quantity_unit="kg",
        unit_price_usd=5.0,
        harvested_date=client.serializer.get_current_timestamp(),
    )
    print(f"   Result: {result.get('status', 'unknown')}")
    print(f"   Message: {result.get('message', '')}")
    time.sleep(1)

if __name__ == "__main__":
    main()
