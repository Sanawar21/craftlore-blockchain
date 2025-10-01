from ..craftlore_client import CraftLoreClient
from models.enums import AccountType, AssetType, ArtisanSkillLevel
import time

def main():
    """Interactive CLI for the client."""
    baap = CraftLoreClient()
    chacha = CraftLoreClient()
    seth = CraftLoreClient()

    print("=" * 60)
    print("CraftLore Combined TP Client")
    print("=" * 60)
    

    emails = {"baap": "ba2ap22.com", "chacha": "cha2cha22.com", "seth": "set2h22.com"}

    print("0. Create Account for chacha")
    account_type = AccountType.ARTISAN
    email = emails["chacha"]
    result = chacha.create_account(
        account_type, 
        email,
        skill_level=ArtisanSkillLevel.INTERMEDIATE,
        years_of_experience=5)
    print(f"   Result: {result.get('status', 'unknown')}")
    print(f"   Message: {result.get('message', '')}")
    time.sleep(1)

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

    print("2. Create Account for Seth")
    account_type = AccountType.SUPPLIER
    email = emails["seth"]
    result = seth.create_account(account_type, email)
    print(f"   Result: {result.get('status', 'unknown')}")
    print(f"   Message: {result.get('message', '')}")
    time.sleep(1)


    print("\n2. Create Work Order Asset by seth")
    asset_type = AssetType.WORK_ORDER
    result = seth.create_asset(
        asset_type,
        assignee=baap.public_key,
        product_description="This is a work order from seth to baap",
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
    time.sleep(1)
    

    print("\n4. Create Sub-Assignment by baap to chacha")
    asset_type = AssetType.SUB_ASSIGNMENT
    result = baap.create_asset(
        asset_type,
        batch=result.get("uid"),  # Link to the batch created from work order
        pay_usd=300.0,
        task_description="Knit 5 wool shawls",
        assignee=chacha.public_key,
    )
    print(f"   Result: {result.get('status', 'unknown')}")
    print(f"   Message: {result.get('message', '')}")

    time.sleep(1)

    print("\n5. Accept Sub-Assignment by chacha")
    assignment_id = result.get("uid")
    if not assignment_id:
        print("   Error: Sub-assignment ID not found, cannot accept sub-assignment.")
        return
    result = chacha.accept_sub_assignment(assignment_id)
    print(f"   Result: {result.get('status', 'unknown')}")
    print(f"   Message: {result.get('message', '')}")

    print("\n6. Complete Sub-Assignment by chacha")
    result = chacha.complete_sub_assignment(assignment_id)
    print(f"   Result: {result.get('status', 'unknown')}")
    print(f"   Message: {result.get('message', '')}")




if __name__ == "__main__":
    main()
