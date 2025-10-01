from ..craftlore_client import CraftLoreClient
from models.enums import AccountType, AssetType, ArtisanSkillLevel
import time

def main():
    """Interactive CLI for the client."""
    baap = CraftLoreClient()
    chacha = CraftLoreClient()
    beta = CraftLoreClient()

    emails = {"baap": "baasdap.com", "chacha": "casdhacha.com", "beta": "betasda.com"}

    print("=" * 60)
    print("CraftLore Combined TP Client")
    print("=" * 60)
    

    print("1. Create Account for baap")
    account_type = AccountType.ARTISAN
    email = emails["baap"]
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
    email = emails["chacha"]
    result = chacha.create_account(account_type, email)
    print(f"   Result: {result.get('status', 'unknown')}")
    print(f"   Message: {result.get('message', '')}")
    time.sleep(1)

    print("3. Create Account for beta")
    account_type = AccountType.ARTISAN
    email = emails["beta"]  
    result = beta.create_account(
        account_type, 
        email,
        skill_level=ArtisanSkillLevel.INTERMEDIATE,
        years_of_experience=5)            
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
    print(f"   Result: {result.get('status', 'unknown')}")
    print(f"   Message: {result.get('message', '')}")
    batch_id = result.get("uid")
    time.sleep(1)
    
    print("\n4. Create Sub-Assignment by baap to beta")
    asset_type = AssetType.SUB_ASSIGNMENT
    result = baap.create_asset(
        asset_type,
        batch=result.get("uid"),  # Link to the batch created from work order
        pay_usd=300.0,
        task_description="Knit 5 wool shawls",
        assignee=beta.public_key,
    )
    print(f"   Result: {result.get('status', 'unknown')}")
    print(f"   Message: {result.get('message', '')}")

    time.sleep(1)

    print("\n5. Accept Sub-Assignment by beta")
    assignment_id = result.get("uid")
    if not assignment_id:
        print("   Error: Sub-assignment ID not found, cannot accept sub-assignment.")
        return
    result = beta.accept_sub_assignment(assignment_id)
    print(f"   Result: {result.get('status', 'unknown')}")
    print(f"   Message: {result.get('message', '')}")


    print("\n4. Complete Work Order by baap (this should fail due to incomplete sub-assignment)")
    result = baap.complete_work_order(work_order_id, units_produced=10)
    print(f"   Result: {result.get('status', 'unknown')}")
    print(f"   Message: {result.get('message', '')}")
    time.sleep(1)

    print("\n5. Complete Sub-Assignment by beta")
    result = beta.complete_sub_assignment(assignment_id)
    print(f"   Result: {result.get('status', 'unknown')}")
    print(f"   Message: {result.get('message', '')}")
    time.sleep(1)

    print("\n6. Complete Work Order by baap (this should succeed now)")
    result = baap.complete_work_order(work_order_id, units_produced=10)
    print(f"   Result: {result.get('status', 'unknown')}")
    print(f"   Message: {result.get('message', '')}")
    time.sleep(1)
    

if __name__ == "__main__":
    main()
