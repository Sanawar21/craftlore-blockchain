#!/usr/bin/env python3
"""
CraftLore asset Transaction Processor
Dedicated TP for managing all account types in the CraftLore blockchain system.
"""

import sys
import argparse
from sawtooth_sdk.processor.core import TransactionProcessor
from sawtooth_sdk.processor.log import init_console_logging

from handler import AssetTransactionHandler


def main():
    """Main entry point for the Account Transaction Processor."""
    parser = argparse.ArgumentParser(
        description='CraftLore Asset Transaction Processor')
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
    handler = AssetTransactionHandler()
    processor.add_handler(handler)

    print("🚀 Starting CraftLore Asset Transaction Processor...")
    print(f"📡 Connecting to validator at: {args.connect}")
    print(f"🏷️  Family: {handler.family_name}")
    print(f"📦 Version: {handler.family_versions[0]}")
    print(f"🔧 Namespace: {handler.namespaces[0]}")
    
    try:
        processor.start()
    except KeyboardInterrupt:
        print("\n--- Asset TP Stopped ---")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
