# CraftLore Combined Transaction Processor

A unified Hyperledger Sawtooth transaction processor that combines both account and asset management for the CraftLore blockchain system. This TP eliminates the need for careful input/output address management by using a single namespace for all operations.

## 🚀 Features

### Unified Namespace
- **Single Family**: `craftlore` (vs separate `craftlore-account` and `craftlore-asset`)
- **Simplified Addressing**: Just use namespace prefix in inputs/outputs
- **No Address Conflicts**: Smart prefix allocation prevents collisions
- **Reduced Complexity**: One TP to manage instead of two

### Account Management
- Create and manage all account types (Supplier, Artisan, Workshop, Distributor, etc.)
- Authentication and authorization workflows
- Account queries and updates
- Privacy-first design with minimal personal data

### Asset Management  
- Raw materials, products, product batches, work orders, warranties
- Asset transfers and ownership tracking
- Workflow operations (lock/unlock, accept/reject)
- Quality certification and sustainability tracking
- Bidirectional relationships between entities

### Business Logic Compliance
- **Supplier Rule**: Only SupplierAccount can create raw material assets
- **Artisan/Workshop Rule**: Only artisan or workshop can be assignee of work orders
- **Flow Enforcement**: Implements all business flows from flow.txt
- **Bidirectional Connections**: Maintains relationships between all entities

## 📁 Project Structure

```
craftlore-tp/
├── core/
│   ├── enums.py          # All system enums (accounts + assets)
│   ├── exceptions.py     # Exception classes
│   └── __init__.py
├── utils/
│   ├── address_generator.py  # Unified address generation
│   ├── serialization.py     # Data serialization helpers
│   └── __init__.py
├── entities/
│   ├── accounts/         # Account entity classes
│   ├── assets/          # Asset entity classes
│   ├── asset_factory.py # Asset creation factory
│   └── __init__.py
├── handlers/
│   ├── account_handler.py    # Account operations
│   ├── asset_creation.py     # Asset creation
│   ├── asset_transfer.py     # Asset transfers
│   ├── asset_workflow.py     # Asset workflows
│   ├── asset_certification.py # Quality & sustainability
│   ├── asset_utils.py        # Shared asset utilities
│   └── __init__.py
├── clients/
│   ├── combined_client.py    # Unified client for all operations
│   └── __init__.py
├── handler.py            # Main transaction handler
├── processor.py          # Transaction processor entry point
├── demo.py              # Complete demo script
├── Dockerfile           # Docker configuration
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## 🎯 Address Architecture

### Namespace: `craftlore`
- **Accounts**: `craftlore + 0x + hash`
- **Raw Materials**: `craftlore + 1x + hash`  
- **Products**: `craftlore + 11 + hash`
- **Product Batches**: `craftlore + 12 + hash`
- **Work Orders**: `craftlore + 13 + hash`
- **Warranties**: `craftlore + 14 + hash`
- **Indices**: `craftlore + fx + hash`

### Benefits
- No address collision between account and asset data
- Easy to identify data type from address prefix
- Simple namespace-only input/output specification
- Automatic state management across all entity types

## 🚀 Quick Start

### 1. Build and Run
```bash
# Build the container
docker build -t craftlore-tp .

# Add to docker-compose.yaml
craftlore-tp:
  build: ./craftlore-tp
  container_name: craftlore-tp
  depends_on:
    - validator
  entrypoint: sleep infinity
  volumes:
    - ./craftlore-tp:/app

# Start services
docker compose up -d

# Run the processor
docker exec -it craftlore-tp python3 processor.py
```

### 2. Run Demo
```bash
# Execute complete demo
docker exec -it craftlore-tp python3 demo.py
```

### 3. Use Client
```python
from clients.combined_client import CraftLoreClient

# Create client
client = CraftLoreClient()

# Create account
result = client.create_account(
    account_type='artisan',
    email='artisan@craftlore.com'
)

# Create raw material (supplier only)
result = client.create_raw_material(
    material_id='wool_001',
    material_type='pashmina_wool',
    supplier_id=client.public_key,
    quantity=100.0,
    source_location='Ladakh'
)

# Create work order
result = client.create_work_order(
    work_order_id='wo_001',
    buyer_id=client.public_key,
    product_batch_id='batch_001',
    assignee_id='artisan_public_key',
    description='Weave shawls'
)
```

## 🔄 Supported Operations

### Account Operations
- `account_create` - Create new account
- `account_authenticate` - Approve/reject accounts  
- `account_update` - Update account information
- `account_deactivate` - Deactivate account
- `account_query` - Query account data

### Asset Operations  
- `create_asset` - Create any asset type
- `transfer_asset` - Transfer ownership
- `bulk_transfer` - Transfer multiple assets
- `accept_asset` - Accept transferred asset
- `lock_asset` / `unlock_asset` - Workflow control
- `update_asset` - Modify asset data
- `delete_asset` - Mark asset as deleted
- `register_warranty` - Add warranty info
- `update_certification` - Quality certification
- `update_sustainability` - Sustainability scores

## 🎯 Business Rules Enforced

1. **Supplier Exclusivity**: Only SupplierAccount can create raw materials
2. **Artisan/Workshop Assignment**: Only artisan or workshop can be work order assignees  
3. **Flow Compliance**: Implements all flows from specification
4. **Bidirectional Links**: Maintains entity relationships in both directions
5. **Authentication Required**: Most operations require approved account status
6. **Ownership Tracking**: Complete provenance and ownership history

## 📊 Advantages Over Separate TPs

### Development Benefits
- **Single Codebase**: Easier maintenance and updates
- **Shared Logic**: Common utilities and patterns
- **Consistent Patterns**: Unified error handling and validation
- **Reduced Duplication**: No repeated code between TPs

### Operational Benefits  
- **Simple Deployment**: One container instead of two
- **Easy Addressing**: No complex input/output management
- **Atomic Operations**: Cross-entity operations in single transaction
- **Better Performance**: No inter-TP communication overhead

### Client Benefits
- **Single Client**: One client handles everything
- **Simplified Integration**: No need to coordinate multiple TPs
- **Consistent API**: All operations follow same patterns
- **Better Error Handling**: Unified error responses

## 🔍 Monitoring and Debugging

### Check TP Status
```bash
# View processor logs
docker logs craftlore-tp

# Check if TP is registered
curl http://localhost:8008/transactions
```

### Query State
```python
# Get all state in namespace
client = CraftLoreClient()
all_state = client.list_all_state()

# Get specific account
account_addr = client.get_account_address(public_key)
account_data = client.get_state(account_addr)

# Get specific asset  
asset_addr = client.get_asset_address(asset_id, asset_type)
asset_data = client.get_state(asset_addr)
```

## 🚦 Migration from Separate TPs

If you were using separate account-tp and asset-tp:

1. **Stop separate TPs**: Stop account-tp and asset-tp processors
2. **Update clients**: Switch to `CraftLoreClient` 
3. **Simplify addressing**: Remove specific address calculations
4. **Use namespace**: Just specify `craftlore` namespace in inputs/outputs
5. **Test operations**: Verify all functionality works as expected

## 📝 Next Steps

This combined TP provides the foundation for the complete CraftLore ecosystem:

- ✅ Account management with privacy compliance
- ✅ Asset lifecycle management  
- ✅ Business rule enforcement
- ✅ Simplified addressing and deployment
- 🔜 Advanced query capabilities
- 🔜 Analytics and reporting features
- 🔜 Integration with frontend applications

The unified approach significantly reduces complexity while maintaining all functionality from the separate transaction processors.
