from ..craftlore_client import CraftLoreClient, AccountType, EventType
import time

def main():
    """Interactive CLI for the client."""
    client = CraftLoreClient()
    
    print("=" * 60)
    print("CraftLore Combined TP Client")
    print("=" * 60)
    
    print("1.Bootstrap System (Create Super Admin Account)")
        
    email = "sa.com"
    result = client.bootstrap(email)
    print(f"   Result: {result.get('status', 'unknown')}")
    print(f"   Message: {result.get('message', '')}")
    time.sleep(1)
            


if __name__ == "__main__":
    main()
