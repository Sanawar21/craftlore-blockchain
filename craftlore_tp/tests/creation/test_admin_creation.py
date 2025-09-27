from ..craftlore_client import CraftLoreClient, AccountType, EventType
from models.enums import AdminPermissionLevel
import time

def main():
    """Interactive CLI for the client."""
    superadmin = CraftLoreClient(private_key="cad4031f9fe3e3af75e067243b370e981c5f6996a829f670ac2e2163b3f2ab26")
    admin = CraftLoreClient()
    imposter = CraftLoreClient()

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
    email = "admin.com"
    permission_level = AdminPermissionLevel.MODERATOR.value
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

    print("3. Attempt to Create Admin Account as Non-Super Admin (Should Fail)")
    email = "badadmin.com"
    permission_level = AdminPermissionLevel.MODERATOR.value
    details = "Attempt to mint a new admin without permissions"
    result = imposter.create_admin(
        public_key=imposter.public_key,
        email=email,
        permission_level=permission_level,
        action_details=details,
        about="I should not be able to do this"
    )
    print(f"   Result: {result.get('status', 'unknown')}")
    print(f"   Message: {result.get('message', '')}")
    time.sleep(1)




if __name__ == "__main__":
    main()
