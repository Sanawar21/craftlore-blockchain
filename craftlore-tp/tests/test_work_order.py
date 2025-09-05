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
    email = "baap.com"
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
    email = "chacha.com"
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
        order_quantity=10,
        total_price=1500.0,
    )
    print(f"   Result: {result.get('status', 'unknown')}")
    print(f"   Message: {result.get('message', '')}")
    time.sleep(1)

if __name__ == "__main__":
    main()
