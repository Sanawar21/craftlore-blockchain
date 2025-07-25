from sawtooth_signing import create_context, CryptoFactory
from sawtooth_signing.secp256k1 import Secp256k1PrivateKey
from sawtooth_sdk.protobuf.transaction_pb2 import TransactionHeader, Transaction
from sawtooth_sdk.protobuf.batch_pb2 import BatchHeader, Batch, BatchList

import requests
import json
from hashlib import sha512


context = create_context('secp256k1')
print(f"Private Key: {context.new_random_private_key().as_hex()}")
private_key = Secp256k1PrivateKey.from_hex(input("Enter your private key (hex): ").strip())

signer = CryptoFactory(context).new_signer(private_key)

action = input("Enter action (write/read): ").strip().lower()

if action not in ['write', 'read']:
    print("Invalid action. Must be 'write' or 'read'.")
    exit(1)
elif action == 'write':
    name = input("Enter name: ").strip()
    if not name:
        print("Name cannot be empty.")
        exit(1)
    payload_bytes = json.dumps({'action': 'write', 'name': name}).encode('utf-8')
else:
    payload_bytes = json.dumps({'action': 'read'}).encode('utf-8')


txn_header_bytes = TransactionHeader(
    family_name='hello_world',
    family_version='1.0',
    inputs=[],
    outputs=[],
    signer_public_key=signer.get_public_key().as_hex(),
    # In this example, we're signing the batch with the same private key,
    # but the batch can be signed by another party, in which case, the
    # public key will need to be associated with that key.
    batcher_public_key=signer.get_public_key().as_hex(),
    # In this example, there are no dependencies.  This list should include
    # an previous transaction header signatures that must be applied for
    # this transaction to successfully commit.
    # For example,
    # dependencies=['540a6803971d1880ec73a96cb97815a95d374cbad5d865925e5aa0432fcf1931539afe10310c122c5eaae15df61236079abbf4f258889359c4d175516934484a'],
    dependencies=[],
    payload_sha512=sha512(payload_bytes).hexdigest()
).SerializeToString()

signature = signer.sign(txn_header_bytes)


txn = Transaction(
    header=txn_header_bytes,
    header_signature=signature,
    payload=payload_bytes
)

txns = [txn]

batch_header_bytes = BatchHeader(
    signer_public_key=signer.get_public_key().as_hex(),
    transaction_ids=[txn.header_signature for txn in txns],
).SerializeToString()

signature = signer.sign(batch_header_bytes)

batch = Batch(
    header=batch_header_bytes,
    header_signature=signature,
    transactions=txns
)


batch_list_bytes = BatchList(batches=[batch]).SerializeToString()

try:
    response = requests.post(
        'http://rest-api:8008/batches',
        headers={'Content-Type': 'application/octet-stream'},
        data=batch_list_bytes
    )
    response.raise_for_status()
    print("Transaction successfully submitted.")
    print(f"Response: {response.json()}")
except requests.exceptions.RequestException as e:
    print(f"Failed to submit transaction: {e}")
    exit(1)