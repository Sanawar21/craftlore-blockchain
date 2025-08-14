#!/usr/bin/env python3
"""
CraftLore Combined Transaction Processor
Unified TP for managing both accounts and assets in the CraftLore blockchain system.
"""

import sys
import argparse
from sawtooth_sdk.processor.core import TransactionProcessor
from sawtooth_sdk.processor.log import init_console_logging

from handler import CraftLoreTransactionHandler


def main():
    """Main entry point for the CraftLore Combined Transaction Processor."""
    parser = argparse.ArgumentParser(
        description='CraftLore Combined Transaction Processor')
    parser.add_argument(
        '-C', '--connect',
        default='tcp://validator:4004',
        help='Endpoint for the validator connection')
    parser.add_argument(
        '-v', '--verbose',
        action='count',
        default=2,
        help='Increase output sent to stderr')
    
    args = parser.parse_args()
    
    # Initialize logging
    init_console_logging(verbose_level=args.verbose)
    
    # Create the transaction processor
    processor = TransactionProcessor(url=args.connect)
    
    # Create and register the handler 
    handler = CraftLoreTransactionHandler()
    processor.add_handler(handler)
    
    print("🚀 Starting CraftLore Combined Transaction Processor...")
    print(f"📡 Connecting to validator at: {args.connect}")
    print(f"🏷️  Family: {handler.family_name}")
    print(f"📦 Version: {handler.family_versions[0]}")
    print(f"🔧 Namespace: {handler.namespaces[0]}")
    print("✅ Handling both Account and Asset operations in unified namespace")
    
    try:
        processor.start()
    except KeyboardInterrupt:
        print("\n--- CraftLore Combined TP Stopped ---")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
