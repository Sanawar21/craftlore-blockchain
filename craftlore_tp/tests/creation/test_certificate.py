from ..craftlore_client import CraftLoreClient, AccountType, AssetType
from models.enums import AdminPermissionLevel
import time

def main():
    """Interactive CLI for the client."""
    superadmin = CraftLoreClient(private_key="cad4031f9fe3e3af75e067243b370e981c5f6996a829f670ac2e2163b3f2ab26")
    admin = CraftLoreClient()
    supplier = CraftLoreClient()

    print("=" * 60)
    print("CraftLore Combined TP Client")
    print("=" * 60)
    
    # print("1.Bootstrap System (Create Super Admin Account)")
        
    # email = "sa.com"
    # result = superadmin.bootstrap(email)
    # print(f"   Result: {result.get('status', 'unknown')}")
    # print(f"   Message: {result.get('message', '')}")
    # time.sleep(1)
            

    print("2. Create Admin Account as Super Admin")
    email = "admi1sns2.com"
    permission_level = AdminPermissionLevel.CERTIFIER.value
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

    print("3. Create supplier")
    email = "suppl1iessr.com"
    result = supplier.create_account(
        account_type=AccountType.SUPPLIER,
        email=email,
    )
    print(f"   Result: {result.get('status', 'unknown')}")
    print(f"   Message: {result.get('message', '')}")
    time.sleep(1)

    print("4. Issue Certification as Admin")
    certificate_id = "CERT12345"
    title = "ISO 9001"
    issue_timestamp = "2024-01-01T00:00:00Z"
    expiry_timestamp = "2027-01-01T00:00:00Z"
    issuer = admin.public_key
    holder = supplier.public_key
    description = "ISO 9001 Quality Management Certification"

    result = admin.issue_certification(
        action_details="Issuing ISO 9001 certificate to supplier",
        certificate_id=certificate_id,
        title=title,
        issue_timestamp=issue_timestamp,
        expiry_timestamp=expiry_timestamp,
        issuer=issuer,
        holder=holder,
        description=description
    )
    print(f"   Result: {result.get('status', 'unknown')}")
    print(f"   Message: {result.get('message', '')}")
    time.sleep(1)

    result = supplier.create_asset(
        asset_type=AssetType.RAW_MATERIAL,
        material_type="Wood",
        quantity=100.0,
        quantity_unit="kg",
        unit_price_usd=5.0,
        harvested_date=supplier.serializer.get_current_timestamp(),
    )
    print(f"   Result: {result.get('status', 'unknown')}")
    print(f"   Message: {result.get('message', '')}")
    time.sleep(1)

    raw_material_id = result.get("uid")
    admin.issue_certification(
        action_details="Issuing ISO 9001 certificate to raw material",
        certificate_id="CERT67890",
        title="ISO 9001 for Raw Material",
        issue_timestamp=issue_timestamp,
        expiry_timestamp=expiry_timestamp,
        issuer=issuer,
        holder=raw_material_id,
        description="ISO 9001 Quality Management Certification for Raw Material"
    )
    print(f"   Result: {result.get('status', 'unknown')}")
    print(f"   Message: {result.get('message', '')}")
    time.sleep(1)



if __name__ == "__main__":
    main()
