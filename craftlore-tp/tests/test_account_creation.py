from .craftlore_client import CraftLoreClient, AccountType, EventType
import time

def main():
    """Interactive CLI for the client."""
    client = CraftLoreClient()
    
    print("=" * 60)
    print("CraftLore Combined TP Client")
    print("=" * 60)
    
    print("\n--- ACCOUNT OPERATIONS ---")
    print("1. Create Account")
        

    account_type = AccountType.SUPPLIER
    email = "sa.com"
    result = client.create_account(account_type, email)
    print(f"   Result: {result.get('status', 'unknown')}")
    print(f"   Message: {result.get('message', '')}")
    time.sleep(1)
            


if __name__ == "__main__":
    main()
