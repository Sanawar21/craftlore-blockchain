#!/usr/bin/env python3
"""
Simple Boilerplate Transaction Processor
A minimal working transaction processor for testing.
"""

import sys
import argparse
from sawtooth_sdk.processor.core import TransactionProcessor
from handler import SimpleTransactionHandler


def main():
    """Main entry point for the transaction processor."""
    
    parser = argparse.ArgumentParser(
        description='Simple Transaction Processor'
    )
    parser.add_argument(
        '-C', '--connect',
        default='tcp://localhost:4004',
        help='Endpoint for the validator connection'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='count',
        default=0,
        help='Increase output sent to stderr'
    )
    
    args = parser.parse_args()
    
    # Set up logging
    if args.verbose > 1:
        import logging
        logging.basicConfig(level=logging.DEBUG)
    elif args.verbose > 0:
        import logging
        logging.basicConfig(level=logging.INFO)
    
    print("🚀 Starting Simple Transaction Processor...")
    print(f"📡 Connecting to validator at: {args.connect}")
    print(f"🏷️  Family: simple")
    print(f"📦 Version: 1.0")
    
    # Create processor and handler
    processor = TransactionProcessor(url=args.connect)
    handler = SimpleTransactionHandler()
    
    # Add handler to processor
    processor.add_handler(handler)
    
    try:
        # Start the processor
        processor.start()
    except KeyboardInterrupt:
        print("\n👋 Shutting down Simple Transaction Processor...")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    finally:
        processor.stop()


if __name__ == '__main__':
    main()
