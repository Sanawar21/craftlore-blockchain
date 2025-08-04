# Transaction Processor Coordination Patterns

## 🚫 **What TPs CANNOT Do**

1. **Direct TP Invocation**: One TP cannot directly call another TP
2. **Cross-TP Transaction Creation**: TPs cannot create transactions for other TPs  
3. **Direct Method Calls**: No API calls between TPs
4. **Shared Memory**: TPs run in separate processes

## ✅ **How TPs CAN Coordinate**

### 1. **Read Each Other's State** 
- **Most Common Pattern**: TPs read blockchain state written by other TPs
- **Use Case**: Product TP validates creator exists in Account TP
- **Implementation**: Use other TP's addressing scheme to read their state

```python
# Product TP reading Account TP state
def validate_creator(self, context, creator_public_key):
    # Use Account TP's addressing scheme
    account_address = AccountAddressGenerator().generate_account_address(creator_public_key)
    entries = context.get_state([account_address])
    
    if entries:
        account_data = json.loads(entries[0].data.decode())
        return account_data.get('authentication_status') == 'approved'
    
    return False
```

### 2. **Event-Based Communication**
- **Pattern**: TPs emit events, external services listen and coordinate
- **Use Case**: Account creation triggers welcome email and profile setup
- **Implementation**: Use `context.add_event()` to emit events

```python
# Account TP emits event
def create_account(self, transaction, context, payload):
    # Create account logic...
    
    # Emit event for other services
    context.add_event(
        event_type='craftlore.account.created',
        attributes=[
            ('public_key', account_data['public_key']),
            ('account_type', account_data['account_type'])
        ]
    )
```

### 3. **Client-Side Orchestration**
- **Pattern**: Client coordinates multiple TPs in sequence
- **Use Case**: Complete artisan onboarding across Account → Product → Verification TPs
- **Implementation**: Client submits transactions to multiple TPs

```python
# Client orchestrates multiple TPs
def onboard_artisan(self, email, specialization):
    # Step 1: Create account
    account_result = self.account_client.create_account('artisan', email)
    
    # Step 2: Setup profile  
    profile_result = self.product_client.setup_artisan_profile(
        account_result['public_key'], specialization
    )
    
    # Step 3: Request verification
    verification_result = self.verification_client.request_initial_verification(
        account_result['public_key']
    )
```

### 4. **Shared State Patterns**
- **Pattern**: TPs coordinate through shared blockchain state conventions
- **Use Case**: Global entity registry, cross-references between entities
- **Implementation**: Common addressing schemes for shared data

```python
# Shared global registry
def store_in_global_registry(self, context, entity_type, public_key, tp_name):
    registry_address = self.generate_global_registry_address(public_key)
    registry_data = {
        'entity_type': entity_type,
        'managing_tp': tp_name,
        'public_key': public_key
    }
    context.set_state({registry_address: json.dumps(registry_data).encode()})
```

## 🏗️ **Best Practices for Multi-TP Architecture**

### **1. Design Principles**
- ✅ **Single Responsibility**: Each TP handles one business domain
- ✅ **Loose Coupling**: TPs should work independently  
- ✅ **Data Consistency**: Use shared state patterns for consistency
- ✅ **Event-Driven**: Use events for loose coordination

### **2. State Design**
- ✅ **Public Key References**: Use public keys to reference entities across TPs
- ✅ **Global Registries**: Maintain shared registries for entity discovery
- ✅ **Bidirectional Relationships**: Store relationships in both directions
- ✅ **Consistent Addressing**: Use predictable addressing schemes

### **3. Coordination Patterns**

| Pattern | When to Use | Example |
|---------|-------------|---------|
| **State Reading** | Validation, entity lookup | Product TP validates account exists |
| **Events** | Async workflows, notifications | Account creation triggers setup |
| **Client Orchestration** | Complex multi-step workflows | Complete purchase process |
| **Shared State** | Entity relationships, global data | Artisan-Product connections |

## 🔄 **CraftLore Multi-TP Architecture**

### **Recommended TP Structure**
1. **Account TP**: User management and authentication
2. **Product TP**: Product creation and inventory  
3. **Verification TP**: Certification and quality control
4. **Transaction TP**: Business transactions and payments
5. **Registry TP**: Global search and indexing

### **Coordination Flows**

#### **Product Creation Flow**
```
1. Account TP: Validate creator account exists and approved
2. Product TP: Create product, reference creator by public key
3. Product TP: Emit product.created event
4. Verification TP: Auto-create verification request (via event listener)
5. Registry TP: Index product for search (via event listener)
```

#### **Purchase Flow**
```
1. Product TP: Reserve product for buyer
2. Transaction TP: Process payment transaction
3. Product TP: Transfer ownership (after payment confirmed)
4. Transaction TP: Emit purchase.completed event
5. External Service: Initiate shipping (via event listener)
```

### **Shared State Architecture**
```python
# Global entity registry (accessible by all TPs)
craftlore-global + hash('entity_registry_' + public_key)

# Cross-references between entities  
craftlore-xref + hash(from_entity + '_' + relationship + '_to')
craftlore-xref + hash(to_entity + '_' + relationship + '_from')

# Global indexes
craftlore-global + hash('type_index_' + entity_type)
craftlore-global + hash('email_index_' + email)
```

## 🚀 **Implementation Examples**

All coordination patterns are implemented in the examples:

- **`cross_tp_state_reading.py`**: How TPs read each other's state
- **`event_based_communication.py`**: Event emission and handling
- **`multi_tp_orchestration.py`**: Client-side coordination workflows  
- **`shared_state_patterns.py`**: Global registries and cross-references

## 🎯 **Summary**

**TPs cannot directly invoke each other**, but they can coordinate effectively through:

1. **Reading shared blockchain state** for validation and entity lookup
2. **Emitting events** for asynchronous workflow coordination  
3. **Client orchestration** for complex multi-step processes
4. **Shared state conventions** for consistent entity relationships

The **CraftLore Account TP** you implemented provides the perfect foundation for this multi-TP architecture, with public keys as primary identifiers and privacy-first design that works seamlessly across all coordination patterns.

**Next Step**: Implement Product TP using these coordination patterns to work with your Account TP!
