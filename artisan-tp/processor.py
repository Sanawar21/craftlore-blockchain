#!/usr/bin/env python3

import sys
import argparse
import logging
from sawtooth_sdk.processor.core import TransactionProcessor
from handler import ArtisanTransactionHandler

def main():
    parser = argparse.ArgumentParser(
        description='Artisan Transaction Processor')
    parser.add_argument('-C', '--connect',
                        default='tcp://validator:4004',
                        help='Endpoint for the validator connection')
    parser.add_argument('-v', '--verbose',
                        action='count',
                        default=0,
                        help='Increase output sent to stderr')
    
    args = parser.parse_args()
    
    # Set up logging based on verbosity
    if args.verbose == 0:
        log_level = logging.WARNING
    elif args.verbose == 1:
        log_level = logging.INFO
    else:
        log_level = logging.DEBUG
    
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=log_level
    )
    
    # Create the transaction processor
    processor = TransactionProcessor(url=args.connect)
    
    # Add the handler
    handler = ArtisanTransactionHandler()
    processor.add_handler(handler)
    
    print("🎨 Starting Artisan Transaction Processor")
    print(f"🔗 Connecting to: {args.connect}")
    print(f"👨‍🎨 Family: {handler.family_name}")
    print(f"📝 Namespaces: {handler.namespaces}")
    
    try:
        processor.start()
    except KeyboardInterrupt:
        print("\n👋 Shutting down gracefully...")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    finally:
        processor.stop()

if __name__ == '__main__':
    main()
