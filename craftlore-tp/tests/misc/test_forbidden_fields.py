from ..craftlore_client import CraftLoreClient, AccountType, EventType, AssetType
import time

def main():
    """Interactive CLI for the client."""
    client = CraftLoreClient()
    
    print("=" * 60)
    print("CraftLore Combined TP Client")
    print("=" * 60)

    forbidden_account_fields = {
        # base class
        "tp_version": "1.0",
        # base account
        "assets": [1, 2, 3],
        # supplier account
        "raw_materials_supplied": ["material1", "material2"],
    }
    

    print("1. Create Account with forbidden fields of supplier")
    account_type = AccountType.SUPPLIER
    email = "beta.com"
    for field, value in forbidden_account_fields.items():
        print(f"   Attempting to set forbidden field '{field}' with value '{value}'")
        result = client.create_account(
            account_type,
            email,
            **{field: value}
            )
        print(f"   Result: {result.get('status', 'unknown')}")
        print(f"   Message: {result.get('message', '')}")
        time.sleep(1)
    time.sleep(1)

    forbidden_asset_fields = {
        # base class
        "tp_version": "1.0",
        # base asset
        "transfer_logistics": ["owner1"],
        # raw material asset
        "processor_public_key": "some_key",
    }

    print("1. Create asset with forbidden fields of supplier")
    asset_type = AssetType.RAW_MATERIAL
    for field, value in forbidden_asset_fields.items():
        print(f"   Attempting to set forbidden field '{field}' with value '{value}'")
        result = client.create_asset(
            asset_type,
            **{field: value},
            material_type="Wood",
            quantity=100.0,
            quantity_unit="kg",
            unit_price_usd=5.0,
            harvested_date=client.serializer.get_current_timestamp(),
        )
        print(f"   Result: {result.get('status', 'unknown')}")
        print(f"   Message: {result.get('message', '')}")
        time.sleep(1)
    # print("\n2. Create Asset")
    # asset_type = AssetType.RAW_MATERIAL
    # result = client.create_asset(
    #     asset_type,
    #     material_type="Wood",
    #     quantity=100.0,
    #     quantity_unit="kg",
    #     unit_price_usd=5.0,
    #     harvested_date=client.serializer.get_current_timestamp(),
    # )
    # print(f"   Result: {result.get('status', 'unknown')}")
    # print(f"   Message: {result.get('message', '')}")
    time.sleep(1)

if __name__ == "__main__":
    main()
