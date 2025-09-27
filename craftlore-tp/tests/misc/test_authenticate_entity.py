from ..craftlore_client import CraftLoreClient, AccountType, AssetType
from models.enums import AdminPermissionLevel, AuthenticationStatus
import time

def main():
    """Interactive CLI for the client."""
    superadmin = CraftLoreClient(private_key="cad4031f9fe3e3af75e067243b370e981c5f6996a829f670ac2e2163b3f2ab26")
    admin = CraftLoreClient()
    client = CraftLoreClient()

    print("=" * 60)
    print("CraftLore Combined TP Client")
    print("=" * 60)
    
    print("1.Bootstrap System (Create Super Admin Account)")
        
    email = "sa.com"
    result = superadmin.bootstrap(email)
    print(f"   Result: {result.get('status', 'unknown')}")
    print(f"   Message: {result.get('message', '')}")
    time.sleep(1)
            

    print("2. Create Admin Account as Super Admin")
    email = "admia21an2.com"
    permission_level = AdminPermissionLevel.AUTHENTICATOR.value
    details = "Mint a new admin for testing"
    result = superadmin.create_admin(
        public_key=admin.public_key,
        email=email,
        permission_level=permission_level,
        action_details=details,
        about="Admin account for moderation"
    )
    print(f"   Result: {result.get('status', 'unknown')}")
    print(f"   Message: {result.get('message', '')}")
    time.sleep(1)

    print("1. Create Account")
    account_type = AccountType.SUPPLIER
    email = "betaaaa.com"
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
    uid = result.get("uid")
    time.sleep(1)

    print("\n3. Authenticate Asset as Admin")
    result = admin.authenticate_asset(uid, AuthenticationStatus.APPROVED.value, "Approving asset as authentic")
    print(f"   Result: {result.get('status', 'unknown')}")
    print(f"   Message: {result.get('message', '')}")
    time.sleep(1)

    print("\n4. Authenticate Account as Admin")
    result = admin.authenticate_account(client.public_key, AuthenticationStatus.APPROVED.value, "Approving account as authentic")
    print(f"   Result: {result.get('status', 'unknown')}")
    print(f"   Message: {result.get('message', '')}")
    time.sleep(1)

if __name__ == "__main__":
    main()
