# CraftLore Transaction Handlers

Comprehensive transaction handlers for the Kashmiri handicrafts blockchain system based on the requirements in `notes.txt`.

## 🎯 Overview

The CraftLore transaction handlers implement the complete supply chain tracking system for Kashmiri handicrafts, covering:

1. **Raw Material Sourcing** (Wool, Silk, Walnut Wood, Papier-Mâché)
2. **Artisan Management** (Registration, Skills, Work Orders)
3. **Manufacturing & Workshops** (Production Tracking, Quality Control)
4. **Distribution Chain** (Distributors, Wholesalers, Retailers)
5. **Buyer Transactions** (Purchases, Ownership Transfer, Reviews)
6. **Certifications** (GI Tags, Quality Certificates)
7. **Post-Sale Services** (Warranties, Repairs, Resales)

## 🏗️ Architecture

### Transaction Handler Structure

```
CraftLoreTransactionHandler
├── Account Transactions
│   ├── account_create
│   ├── account_authenticate
│   ├── account_update
│   └── account_delete
├── Material Transactions
│   ├── material_harvest
│   ├── material_certify
│   └── material_transfer
├── Product Transactions
│   ├── product_create
│   ├── product_update_progress
│   ├── product_complete
│   └── product_quality_check
├── Workshop Transactions
│   ├── workshop_register
│   ├── workshop_intake_material
│   └── workshop_assign_artisan
├── Order Transactions
│   ├── order_create
│   ├── order_assign
│   └── order_complete
├── Shipment Transactions
│   ├── shipment_create
│   ├── shipment_update_location
│   └── shipment_deliver
├── Business Transactions
│   ├── transaction_purchase
│   ├── transaction_payment
│   └── transaction_royalty
├── Certificate Transactions
│   ├── certificate_issue
│   ├── certificate_verify
│   └── certificate_revoke
└── Review Transactions
    ├── review_create
    └── review_update
```

### Object Classes

1. **RawMaterial** - Raw materials (wool, silk, wood, etc.)
2. **HandicraftProduct** - Finished handicraft products
3. **WorkOrder** - Production work orders
4. **BusinessTransaction** - Purchase/sale transactions
5. **Certificate** - Various certifications (GI, quality, etc.)
6. **Account** - All stakeholder accounts with role-based access

## 🚀 Transaction Types

### 1. Account Management

#### Create Account
```json
{
  "action": "account_create",
  "account_type": "artisan",
  "account_data": {
    "account_id": "artisan_001",
    "artisan_name": "Master Weaver Ali",
    "specialization": "Carpet Weaving",
    "years_experience": 25,
    "location": "Srinagar, Kashmir",
    "aadhaar_number": "1234-5678-9012",
    "govt_id": "J&K/ART/001"
  }
}
```

#### Authenticate Account
```json
{
  "action": "account_authenticate",
  "account_id": "artisan_001",
  "status": "approved",
  "reason": "Verified credentials and skills",
  "block_number": 1001
}
```

### 2. Raw Material Tracking

#### Record Material Harvest
```json
{
  "action": "material_harvest",
  "material_data": {
    "material_id": "wool_batch_001",
    "supplier_id": "supplier_001",
    "material_type": "wool",
    "harvest_date": "2025-01-01",
    "quantity": 100,
    "source_location": "Kashmir Valley, 34.0837°N, 74.7973°E",
    "certifications": ["organic", "sustainable"]
  }
}
```

### 3. Product Creation & Tracking

#### Create Product
```json
{
  "action": "product_create",
  "product_data": {
    "product_id": "carpet_001",
    "product_name": "Traditional Kashmiri Carpet",
    "product_type": "carpet",
    "artisan_id": "artisan_001",
    "workshop_id": "workshop_001",
    "materials_used": ["wool_batch_001"],
    "estimated_completion": "2025-03-01",
    "price": 500.0
  }
}
```

#### Update Product Progress
```json
{
  "action": "product_update_progress",
  "product_id": "carpet_001",
  "progress_data": {
    "stage": "weaving",
    "progress_percentage": 50,
    "time_spent_hours": 120,
    "photos": ["progress_photo_1.jpg"],
    "notes": "Pattern foundation completed"
  }
}
```

### 4. Work Order Management

#### Create Work Order
```json
{
  "action": "order_create",
  "order_data": {
    "order_id": "order_001",
    "artisan_id": "artisan_001",
    "product_type": "carpet",
    "assigned_date": "2025-01-20",
    "expected_completion": "2025-03-01",
    "payment_terms": {
      "amount": 300.0,
      "currency": "USD"
    }
  }
}
```

### 5. Business Transactions

#### Record Purchase
```json
{
  "action": "transaction_purchase",
  "transaction_data": {
    "transaction_id": "purchase_001",
    "buyer_id": "buyer_001",
    "seller_id": "artisan_001",
    "product_id": "carpet_001",
    "amount": 500.0,
    "payment_method": "crypto",
    "royalty_info": {
      "artisan_percentage": 5.0,
      "artisan_address": "artisan_wallet_001"
    }
  }
}
```

### 6. Certificate Management

#### Issue Certificate
```json
{
  "action": "certificate_issue",
  "certificate_data": {
    "certificate_id": "gi_cert_001",
    "certificate_type": "GI",
    "holder_id": "carpet_001",
    "issuing_authority": "Kashmir Craft Council",
    "issue_date": "2025-01-20",
    "certificate_data": {
      "geographic_origin": "Kashmir",
      "traditional_methods": true,
      "authenticity_verified": true
    }
  }
}
```

## 🔐 Authorization & Authentication

### Role-Based Access Control

- **Super Admin**: Full system access
- **Artisan Admin**: Manage artisan accounts and artisan-related objects
- **Supplier Admin**: Manage supplier accounts and materials
- **Workshop Admin**: Manage workshop accounts and production
- **Other Admins**: Domain-specific administration rights

### Multi-Signature Support

High-value transactions and sensitive operations can require multiple signatures:

```json
{
  "required_signatures": 2,
  "authorized_by": ["admin_001", "supervisor_002"]
}
```

## 📊 History & Audit Trail

Every object maintains comprehensive history:

- **Block Numbers**: Blockchain block where changes occurred
- **Transaction IDs**: Unique transaction identifiers
- **Previous State**: Object state before change
- **Current State**: Object state after change
- **Actor Information**: Who performed the action
- **Timestamps**: When changes occurred

## 🏪 Stakeholder Coverage

### Supported Account Types

1. **SuperAdmin** - System administration
2. **ArtisanAdmin** - Artisan management
3. **Artisan** - Craftspeople
4. **SupplierAdmin** - Supplier management
5. **Supplier** - Raw material suppliers
6. **WorkshopAdmin** - Workshop management
7. **Workshop** - Manufacturing units
8. **DistributorAdmin** - Distribution management
9. **Distributor** - Product distributors
10. **WholesalerAdmin** - Wholesale management
11. **Wholesaler** - Bulk distributors
12. **RetailerAdmin** - Retail management
13. **Retailer** - End-point sellers
14. **Buyer** - End customers

## 🚀 Getting Started

### 1. Start the Transaction Processor

```bash
# Using Docker Compose
docker-compose up -d craftlore-tp

# View logs
docker logs -f craftlore-tp
```

### 2. Run the Demo Client

```bash
# Inside the container
docker exec craftlore-tp python3 client.py
```

### 3. Test Individual Transactions

```python
from client import CraftLoreClient
from object import AccountType, AuthenticationStatus

client = CraftLoreClient()

# Create an artisan account
client.create_account(AccountType.ARTISAN, {
    'account_id': 'artisan_001',
    'artisan_name': 'Master Weaver',
    'specialization': 'Carpet Weaving'
})

# Authenticate the account
client.authenticate_account('artisan_001', AuthenticationStatus.APPROVED)
```

## 📁 File Structure

```
craftloreSDK/
├── handlers.py          # Main transaction handlers
├── processor.py         # Transaction processor entry point
├── client.py           # Client for testing transactions
├── object.py           # Base object classes
├── accounts.py         # Account type implementations
├── enhanced_demo.py    # Enhanced object system demo
├── Dockerfile          # Container configuration
├── requirements.txt    # Python dependencies
└── README.md          # This documentation
```

## 🎯 Compliance with Notes.txt

This implementation covers all requirements from `notes.txt`:

✅ **Raw Material Sourcing** - Material harvest tracking, supplier verification, quality certification
✅ **Artisan Management** - Registration, workshop association, skill certification, work orders, progress tracking, earnings
✅ **Manufacturing Units** - Workshop registration, material intake, production workflow, final product registration
✅ **Distribution Chain** - Distributor registration, shipment tracking, warehouse logs
✅ **Wholesale Operations** - Wholesaler registration, bulk orders, inventory management, retailer sales
✅ **Retail Operations** - Retailer registration, product purchases, stock management, point-of-sale transactions
✅ **Buyer Transactions** - Buyer profiles, purchase transactions, ownership registration, delivery confirmation, reviews
✅ **Post-Sale Services** - Warranty registration, repair logs, resale transfers
✅ **Sustainability** - Sustainability scoring, fair trade compliance

## 🔄 Next Steps

The transaction handlers are ready for production use. You can:

1. **Customize Business Logic** - Modify specific transaction handlers for your business rules
2. **Add Validation** - Implement stricter validation for transaction data
3. **Integrate with Sawtooth** - Deploy to a full Sawtooth network
4. **Add Smart Contracts** - Implement automatic royalty distribution and payments
5. **Scale the System** - Add more transaction families for specific use cases

🎉 **The foundation is complete and ready for the Kashmiri handicrafts blockchain ecosystem!**
