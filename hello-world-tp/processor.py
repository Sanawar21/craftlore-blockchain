from sawtooth_sdk.processor.core import TransactionProcessor
from handler import HelloWorldTransactionHandler
import logging

def main():
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # In docker, the url would be the validator's container name with
    # port 4004
    processor = TransactionProcessor(url='tcp://sawtooth-validator-default:4004')

    handler = HelloWorldTransactionHandler()

    processor.add_handler(handler)
    
    print("Starting Hello World Transaction Processor...")
    print(f"Connecting to validator at: tcp://sawtooth-validator-default:4004")
    print(f"Family: {handler.family_name}")
    print(f"Namespaces: {handler.namespaces}")

    try:
        processor.start()
    except KeyboardInterrupt:
        print("Shutting down...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        processor.stop()

if __name__ == '__main__':
    main()

    # 8ae092449e649b440fd4872509f3a7f7ab041931261943b3e44b6119059190e2