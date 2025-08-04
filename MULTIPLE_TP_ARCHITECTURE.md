# CraftLore Multiple Transaction Processors Architecture

## Recommended TP Structure

### 1. **Account TP** (`craftlore-account`)
- **Purpose**: User account management and authentication
- **Actions**: `account_create`, `account_authenticate`, `account_update`, `account_deactivate`
- **Entities**: Buyers, Sellers, Admins, SuperAdmins, Verifiers
- **Namespace**: `craftlore-account`

### 2. **Product TP** (`craftlore-product`)
- **Purpose**: Product catalog and inventory management
- **Actions**: `product_create`, `product_update`, `material_register`, `workshop_register`
- **Entities**: Products, Materials, Workshops, Categories
- **Namespace**: `craftlore-product`

### 3. **Verification TP** (`craftlore-verification`)
- **Purpose**: Product authenticity and certification
- **Actions**: `verification_request`, `verification_complete`, `certificate_issue`
- **Entities**: Verifications, Certificates, Authenticity Records
- **Namespace**: `craftlore-verification`

### 4. **Transaction TP** (`craftlore-transaction`)
- **Purpose**: Business transactions and payments
- **Actions**: `order_create`, `payment_process`, `shipment_track`
- **Entities**: Orders, Payments, Shipments, Invoices
- **Namespace**: `craftlore-transaction`

### 5. **Registry TP** (`craftlore-registry`)
- **Purpose**: System-wide registries and lookups
- **Actions**: `registry_update`, `index_maintain`, `search_execute`
- **Entities**: Indices, Registries, Search Results
- **Namespace**: `craftlore-registry`

## TP Implementation Structure

```
craftlore-sawtooth-dev/
├── account-tp/
│   ├── processor.py          # Account TP entry point
│   ├── handler.py           # Account transaction handler
│   ├── entities/            # Account entities
│   └── Dockerfile           # Account TP container
├── product-tp/
│   ├── processor.py          # Product TP entry point
│   ├── handler.py           # Product transaction handler
│   ├── entities/            # Product entities
│   └── Dockerfile           # Product TP container
├── verification-tp/
│   ├── processor.py          # Verification TP entry point
│   ├── handler.py           # Verification transaction handler
│   ├── entities/            # Verification entities
│   └── Dockerfile           # Verification TP container
├── transaction-tp/
│   ├── processor.py          # Transaction TP entry point
│   ├── handler.py           # Transaction transaction handler
│   ├── entities/            # Transaction entities
│   └── Dockerfile           # Transaction TP container
├── registry-tp/
│   ├── processor.py          # Registry TP entry point
│   ├── handler.py           # Registry transaction handler
│   ├── entities/            # Registry entities
│   └── Dockerfile           # Registry TP container
└── shared/
    ├── core/                # Shared core classes
    ├── utils/               # Shared utilities
    └── entities/            # Shared base entities
```

## Benefits of Multiple TPs

### 1. **Operational Benefits**
- **Independent Scaling**: Scale account TP during registration surges
- **Selective Updates**: Update product TP without affecting payments
- **Resource Optimization**: Allocate resources based on TP load
- **Monitoring Granularity**: Track performance per business domain

### 2. **Development Benefits**
- **Team Autonomy**: Different teams own different TPs
- **Parallel Development**: Work on multiple TPs simultaneously
- **Technology Flexibility**: Use different libraries per TP if needed
- **Testing Isolation**: Test each TP independently

### 3. **Business Benefits**
- **Feature Rollout**: Roll out new features per domain
- **Risk Mitigation**: Limit blast radius of issues
- **Compliance**: Meet different regulatory requirements per TP
- **Performance**: Optimize each TP for its specific workload

## Cross-TP Communication

### **Shared State Access**
```python
# Each TP can read state from other TPs
def get_account_info(context, account_id):
    account_address = generate_address('craftlore-account', account_id)
    return context.get_state([account_address])

def validate_product_exists(context, product_id):
    product_address = generate_address('craftlore-product', product_id)
    return len(context.get_state([product_address])) > 0
```

### **Event System**
```python
# TPs can emit events for other TPs to consume
context.add_event(
    event_type='account.created',
    attributes=[
        ('account_id', account_id),
        ('account_type', account_type)
    ]
)
```

## Deployment Configuration

### **Docker Compose Setup**
```yaml
version: '3.7'
services:
  account-tp:
    build: ./account-tp
    depends_on:
      - validator
    command: account-tp -v tcp://validator:4004

  product-tp:
    build: ./product-tp
    depends_on:
      - validator
    command: product-tp -v tcp://validator:4004

  verification-tp:
    build: ./verification-tp
    depends_on:
      - validator
    command: verification-tp -v tcp://validator:4004

  transaction-tp:
    build: ./transaction-tp
    depends_on:
      - validator
    command: transaction-tp -v tcp://validator:4004

  registry-tp:
    build: ./registry-tp
    depends_on:
      - validator
    command: registry-tp -v tcp://validator:4004
```

## Migration Strategy

### **Phase 1: Extract Account TP**
1. Create standalone account-tp from current modular code
2. Deploy alongside existing monolithic TP
3. Gradually route account transactions to new TP

### **Phase 2: Extract Product TP**
1. Build product-tp with product/material/workshop logic
2. Test cross-TP communication with account-tp
3. Route product transactions to new TP

### **Phase 3: Extract Remaining TPs**
1. Continue with verification-tp and transaction-tp
2. Create registry-tp for indexing and search
3. Deprecate monolithic TP

### **Phase 4: Optimization**
1. Fine-tune each TP for its workload
2. Implement advanced cross-TP patterns
3. Add TP-specific monitoring and alerting

## Conclusion

**Yes, you should create multiple TPs** for CraftLore. The modular refactoring you've already done provides an excellent foundation - each handler can easily become its own TP. This approach provides better scalability, maintainability, and operational flexibility for a production blockchain system.
