# python3 -m tests.misc.exhaustive
from ..craftlore_client import CraftLoreClient
from models.enums import AdminPermissionLevel, AccountType, ArtisanSkillLevel, AuthenticationStatus, AssetType
import time

def process_result(result):
    print(f"   Result: {result.get('status', 'unknown')}")
    message = result.get('message', '')
    if message:
        print(f"   Message: {message}")
    if "uid" in result:
        print(f"Asset UID: {result.get('uid')}")
    time.sleep(1)

def main():
    """Interactive CLI for the client."""
    super_admin = CraftLoreClient(private_key="cad4031f9fe3e3af75e067243b370e981c5f6996a829f670ac2e2163b3f2ab26")
    authenticator = CraftLoreClient()
    lab_certifier = CraftLoreClient()
    govt_certifier = CraftLoreClient()
    supplier = CraftLoreClient()
    artisan = CraftLoreClient()
    sub_artisan = CraftLoreClient()
    buyer = CraftLoreClient()

    emails = {
        "super_admin": "sa.com",
        "authenticator": "authenticator.com",
        "lab_certifier": "lab_certifier.com",
        "govt_certifier": "govt_certifier.com",
        "supplier": "supplier.com",
        "artisan": "artisan.com",
        "sub_artisan": "sub_artisan.com",
        "buyer": "buyer.com",
    }

    print("=" * 60)
    print("CraftLore Combined TP Client")
    print("=" * 60)

    print("Stage 1: Create Admin accounts")
    print("-" * 60)
    time.sleep(1)
    
    print("1.Bootstrap System (Create Super Admin Account)")
    email = emails["super_admin"]
    result = super_admin.bootstrap(email)
    process_result(result)

    print("2. Create authenticator admin")
    email = emails["authenticator"]
    result = super_admin.create_admin(
        public_key=authenticator.public_key,
        email=email,
        permission_level=AdminPermissionLevel.AUTHENTICATOR.value,
        action_details="Mint a new authenticator admin for testing",
        about="Authenticator admin account which will authenticate the data on the blockchain"
    )
    process_result(result)
            
    print("3. Create lab certifier admin")
    email = emails["lab_certifier"]
    result = super_admin.create_admin(
        public_key=lab_certifier.public_key,
        email=email,
        permission_level=AdminPermissionLevel.CERTIFIER.value,
        action_details="Mint a new lab certifier admin for testing",
        about="Lab certifier admin account which will provide lab certificates on the blockchain"
    )
    process_result(result)

    print("4. Create govt certifier admin")
    email = emails["govt_certifier"]
    result = super_admin.create_admin(
        public_key=govt_certifier.public_key,
        email=email,
        permission_level=AdminPermissionLevel.CERTIFIER.value,
        action_details="Mint a new govt certifier admin for testing",
        about="Govt certifier admin account which will provide govt certificates on the blockchain"
    )
    process_result(result)

    print("Stage 2: Create user accounts")
    print("-" * 60)
    time.sleep(1)

    print("5. Create supplier account")
    email = emails["supplier"]
    result = supplier.create_account(
        account_type=AccountType.SUPPLIER,
        email=email,
        supplier_type="Wool and Fabric supplier",
        region="Kashmir",
        specializations=["Wool", "Fabric"],
    )
    process_result(result)

    print("6. Create artisan account")
    email = emails["artisan"]
    result = artisan.create_account(
        account_type=AccountType.ARTISAN,
        email=email,
        skill_level=ArtisanSkillLevel.EXPERT,
        craft_categories=["Textiles", "Handicrafts"],
        years_of_experience=10,
        traditional_techniques=["Hand Weaving", "Embroidery"],
    )
    process_result(result)

    print("6.1 Create sub-artisan account")
    email = emails["sub_artisan"]
    result = sub_artisan.create_account(
        account_type=AccountType.ARTISAN,
        email=email,
        skill_level=ArtisanSkillLevel.INTERMEDIATE,
        craft_categories=["Textiles"],
        years_of_experience=5,
        traditional_techniques=["Hand Weaving"],
    )
    process_result(result)

    print("7. Create buyer account")
    email = emails["buyer"]
    result = buyer.create_account(
        account_type=AccountType.BUYER,
        email=email,
        region="US",
    )
    process_result(result)

    print("Stage 3: Authenticate stakeholder accounts")
    print("-" * 60)
    time.sleep(1)
    
    print("8. Authenticate supplier account")
    result = authenticator.authenticate_account(
        supplier.public_key,
        AuthenticationStatus.APPROVED,
        action_details="Authenticating supplier account after thorough verification",
    )
    process_result(result)

    print("9. Authenticate artisan account")
    result = authenticator.authenticate_account(
        artisan.public_key,
        AuthenticationStatus.APPROVED,
        action_details="Authenticating artisan account after thorough verification",
    )
    process_result(result)

    print("9.1 Authenticate sub-artisan account")
    result = authenticator.authenticate_account(
        sub_artisan.public_key,
        AuthenticationStatus.APPROVED,
        action_details="Authenticating sub-artisan account after thorough verification",
    )
    process_result(result)

    print("10. Authenticate buyer account")
    result = authenticator.authenticate_account(
        buyer.public_key,
        AuthenticationStatus.APPROVED,
        action_details="Authenticating buyer account after thorough verification",
    )
    process_result(result)

    print("Stage 4: User Flow")
    print("-" * 60)
    time.sleep(1)
    
    print("11. Supplier creates raw material asset")
    result = supplier.create_asset(
        asset_type=AssetType.RAW_MATERIAL,
        material_type="Wool",
        quantity=100.0,
        quantity_unit="kg",
        unit_price_usd=50.0,
        harvested_date="2023-10-01",
        source_location="Kashmir",
    )
    process_result(result)
    raw_material_id = result.get("uid")

    print("12. Lab certifier certifies the raw material")
    result = lab_certifier.issue_certification(
        action_details="Issuing ISO 9001 certificate to raw material",
        title="ISO 9001 for Raw Material",
        issue_timestamp="2024-01-01T00:00:00Z",
        expiry_timestamp="2027-01-01T00:00:00Z",
        holder=raw_material_id,
        description="ISO 9001 Quality Management Certification for Raw Material after lab testing"
    )
    process_result(result)

    print("13. Buyer creates work order for artisan.")
    asset_type = AssetType.WORK_ORDER
    result = buyer.create_asset(
        asset_type,
        assignee=artisan.public_key,
        product_description="This is a work order from buyer to artisan",
        requested_quantity=10,
        requested_quantity_unit="pieces",
        total_price_usd=1500.0,
    )
    process_result(result)
    work_order_id = result.get("uid")

    print("14. Artisan accepts the work order.")
    result = artisan.accept_work_order(work_order_id)
    process_result(result)
    batch_id = result.get("uid")

    print("15. Supplier transfers raw material to artisan after artisan purchases it off chain.")
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
    process_result(result)

    print("16. Artisan adds raw material to batch.")
    result = artisan.add_raw_material_to_batch(
        batch_id,
        raw_material_id,
        50
    )
    process_result(result)

    print("17. Artisan creates subassignment to sub-artisan.")
    result = artisan.create_asset(
        asset_type=AssetType.SUB_ASSIGNMENT,
        batch=batch_id,
        pay_usd=300.0,
        task_description="Knit 5 wool shawls",
        assignee=sub_artisan.public_key,
    )
    process_result(result)
    sub_assignment_id = result.get("uid")

    print("18. Sub-artisan accepts the sub-assignment.")
    result = sub_artisan.accept_sub_assignment(sub_assignment_id)
    process_result(result)

    print("19. Artisan marks the work order as completed (after receiving products from sub-artisan).")
    result = artisan.complete_work_order(
        work_order_id,
        units_produced=10,
    )
    process_result(result)

    print("19.1 Products are certified by govt certifier.")
    for i in range(1, 11):
        product_id = f"{batch_id}-{i}"
        result = govt_certifier.issue_certification(
            action_details="Issuing GI certificate to the finished product",
            title="GI Certificate for Handwoven Wool Shawl",
            issue_timestamp="2024-01-15T00:00:00Z",
            expiry_timestamp="2029-01-15T00:00:00Z",
            holder=product_id,
            description="Geographical Indication (GI) Certification for Handwoven Wool Shawl from Kashmir",
            fields={
                "gi_registration_number": "GI123456789",
                "region": "Kashmir",
                "product_type": "Handwoven Wool Shawl",
                "certifying_authority": "Govt of India"
            }
        )
        process_result(result)

    print("20. Artisan packages the products.")
    result = artisan.create_asset(
        AssetType.PACKAGING,
        products=[f"{batch_id}-{i}" for i in range(1,11)],
        package_type="Box",
        materials_used=["Cardboard", "Tape"],
        labelling={"label": "Fragile"},
        seal_id="SEAL12345",
        net_weight=5.0,
        gross_weight=5.5,
        package_width=30.0,
        package_height=20.0,
        price_usd=1500
    )
    process_result(result)
    package_id = result.get("uid")

    print("21. Artisan transfers package to buyer. (after payment off-chain)")
    result = artisan.transfer_assets(
        [package_id],
        recipient=buyer.public_key,
        logistics={            
            "carrier": "DHL",
            "tracking_id": "DHL123456789",
            "origin": "Supplier Warehouse, City A",
            "destination": "Artisan Workshop, City B",
            "dispatch_date": artisan.serializer.get_current_timestamp(),
            "estimated_delivery_date": artisan.serializer.get_current_timestamp(),
            "freight_cost_usd": 50.0
        }
      )
    process_result(result)

if __name__ == "__main__":
    main()
