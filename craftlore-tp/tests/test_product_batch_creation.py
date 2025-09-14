from .craftlore_client import CraftLoreClient, AccountType, EventType, AssetType
import time
from models.enums import AccountType, AssetType, ArtisanSkillLevel

def main():
    """Interactive CLI for the client."""
    client = CraftLoreClient()
    
    print("=" * 60)
    print("CraftLore Combined TP Client")
    print("=" * 60)
    

    print("1. Create Account")
    account_type = AccountType.ARTISAN
    email = "beta.com"
    result = client.create_account(account_type, email,skill_level=ArtisanSkillLevel.EXPERT,
        years_of_experience=10)
    print(f"   Result: {result.get('status', 'unknown')}")
    print(f"   Message: {result.get('message', '')}")
    time.sleep(1)
            
    print("\n2. Create Asset")
    asset_type = AssetType.PRODUCT_BATCH
    result = client.create_asset(
        asset_type,
        quantity=100,
        unit="pieces",
        product_description="wool shawls",
    )
    print(f"   Result: {result.get('status', 'unknown')}")
    print(f"   Message: {result.get('message', '')}")
    time.sleep(1)

if __name__ == "__main__":
    main()