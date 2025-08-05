# CraftLore Account Transaction Processor

A dedicated Hyperledger Sawtooth Transaction Processor for managing all account types in the CraftLore blockchain system with privacy-first design principles.

## 🎯 Overview

The Account TP handles user account management for the CraftLore handicraft authentication and supply chain system. It implements a privacy-first approach where only email addresses are stored as personal data on-chain, with all sensitive information managed off-chain.

## 🏗️ Architecture

### Account Types Supported

1. **BuyerAccount** - Customers purchasing handicrafts
2. **SellerAccount** - Basic handicraft sellers
3. **ArtisanAccount** - Handicraft creators with detailed craft tracking
4. **WorkshopAccount** - Craft production facilities
5. **DistributorAccount** - Logistics and distribution services
6. **WholesalerAccount** - Bulk handicraft trading
7. **RetailerAccount** - Direct-to-consumer sales
8. **VerifierAccount** - Certification and authentication services
9. **AdminAccount** - System management and oversight
10. **SuperAdminAccount** - Full system access and control

### Privacy-First Design

✅ **On-Chain Data (Safe to Store)**:
- Public keys (primary identifiers)
- Email addresses (only personal data - for off-chain linking)
- Professional/business data (with consent)
- Transaction/production data (anonymous)
- Aggregate compliance metrics

❌ **Off-Chain Data (Secure External Storage)**:
- Personal identity information
- Financial sensitive data
- Business sensitive information
- Personal behavioral data

## 🚀 Features

### Core Operations
- **Account Creation**: Create accounts for all supported types
- **Authentication**: Admin approval/rejection of new accounts
- **Account Updates**: Modify account information
- **Account Deactivation**: Disable accounts when needed
- **Account Queries**: Search by public key, email, or account type

### Security Features
- **Public Key Authentication**: Cryptographic identity verification
- **Permission Hierarchy**: Role-based access control
- **Bootstrap Protection**: Special handling for first SuperAdmin
- **Audit Trail**: Complete history of account changes

### Privacy Features
- **Email-Only Personal Data**: Minimal on-chain personal information
- **Off-Chain Integration**: Ready for secure external authentication
- **GDPR Compliance**: Right to be forgotten support
- **Data Minimization**: Store only necessary professional data

## 📁 Project Structure

```
account-tp/
├── processor.py              # Main TP entry point
├── handler.py               # Transaction handler logic
├── client.py                # Test client and demo
├── requirements.txt         # Python dependencies
├── Dockerfile              # Container configuration
├── core/
│   ├── enums.py            # Account types and status enums
│   └── exceptions.py       # Custom exception classes
├── utils/
│   ├── address_generator.py # Blockchain address generation
│   └── serialization.py    # JSON serialization helpers
└── entities/
    └── accounts/
        ├── base_account.py  # Base account class
        └── __init__.py     # All specific account classes
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- Hyperledger Sawtooth validator running
- Docker (optional)

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run the Transaction Processor
```bash
python processor.py -v -C tcp://localhost:4004
```

### Run with Docker
```bash
# Build the image
docker build -t craftlore-account-tp .

# Run the container
docker run --network host craftlore-account-tp -v -C tcp://localhost:4004
```

## 📊 Usage Examples

### Create Accounts

```python
from client import AccountTPClient

client = AccountTPClient()

# Create SuperAdmin (bootstrap)
result = client.create_account(
    account_type='super_admin',
    email='admin@craftlore.com'
)

# Create Artisan
result = client.create_account(
    account_type='artisan',
    email='artisan@craftlore.com',
    specialization=['carpet_weaving'],
    skill_level='master_craftsman',
    years_experience=15
)

# Create Workshop
result = client.create_account(
    account_type='workshop',
    email='workshop@craftlore.com',
    workshop_type='traditional_weaving',
    capacity_artisans=25
)
```

### Authentication & Management

```python
# Authenticate an account (admin only)
result = client.authenticate_account(
    target_public_key='artisan_public_key_here',
    auth_decision='approve'
)

# Update account information
result = client.update_account(
    specialization=['carpet_weaving', 'contemporary_designs']
)

# Query accounts
result = client.query_account_by_email('artisan@craftlore.com')
result = client.query_accounts_by_type('artisan')
```

## 🔐 Security Model

### Permission Hierarchy

1. **SuperAdmin**: Full system access, can manage all account types
2. **Admin**: Can authenticate and manage non-admin accounts
3. **Users**: Can update their own accounts only

### Authentication Flow

1. User creates account → Status: PENDING
2. Admin reviews and approves/rejects
3. Approved accounts can use full system features
4. Rejected accounts have limited access

### Bootstrap Security

- First SuperAdmin account is auto-approved (system bootstrap)
- Subsequent SuperAdmins must be created by existing SuperAdmins
- Bootstrap status is tracked on-chain

## 🌐 API Reference

### Transaction Family Details
- **Family Name**: `craftlore-account`
- **Version**: `1.0`
- **Namespace**: First 6 characters of SHA-512 hash of family name

### Supported Actions

| Action | Description | Required Fields | Permissions |
|--------|-------------|----------------|-------------|
| `account_create` | Create new account | `account_type`, `email` | Anyone |
| `account_authenticate` | Approve/reject account | `target_public_key`, `auth_decision` | Admin+ |
| `account_update` | Update account info | Account-specific fields | Self/Admin+ |
| `account_deactivate` | Disable account | `target_public_key` | Admin+ |
| `account_query` | Query account data | Query-specific fields | Anyone |

### Address Generation

- **Account Data**: `{namespace}{00}{sha512(public_key)[:62]}`
- **Email Index**: `{namespace}{01}{sha512(email)[:62]}`
- **Type Index**: `{namespace}{02}{sha512(account_type)[:62]}`
- **Bootstrap**: `{namespace}{03}{sha512('bootstrap_complete')[:62]}`

## 🧪 Testing

### Run Demo Client
```bash
python client.py
```

This will run a comprehensive test suite that:
1. Creates a SuperAdmin account (bootstrap)
2. Creates various account types
3. Tests authentication workflows
4. Demonstrates query operations
5. Shows update functionality

### Test Scenarios

The demo covers:
- ✅ Account creation for all types
- ✅ Bootstrap scenario handling
- ✅ Admin authentication workflows
- ✅ Permission validation
- ✅ Query operations (by key, email, type)
- ✅ Account updates and modifications
- ✅ Error handling and validation

## 🔗 Integration

### With Other TPs

The Account TP is designed to work with other CraftLore TPs:

- **Product TP**: References account public keys for product creators
- **Verification TP**: Links to verifier accounts for certifications
- **Transaction TP**: Uses account public keys for business transactions

### Off-Chain Integration

```python
# Example off-chain authentication service integration
class OffChainAuthService:
    def link_identity_to_blockchain(self, email: str, verified_identity: Identity):
        # Store sensitive data encrypted off-chain
        encrypted_profile = encrypt_with_key({
            'full_name': verified_identity.full_name,
            'phone': verified_identity.phone,
            'address': verified_identity.address,
            # All sensitive data
        })
        
        # Link via email to blockchain account
        blockchain_account = query_account_by_email(email)
        
        return {
            'blockchain_account': blockchain_account,
            'off_chain_profile': encrypted_profile
        }
```

## 📈 Monitoring & Metrics

The Account TP tracks:
- Account creation rates by type
- Authentication approval rates
- Query performance metrics
- Error rates and types
- Bootstrap status

## 🔧 Configuration

### Environment Variables

- `VALIDATOR_URL`: Sawtooth validator endpoint (default: tcp://localhost:4004)
- `LOG_LEVEL`: Logging level (default: INFO)

### Customization

Account types and their specific fields can be extended by:
1. Adding new AccountType enum values
2. Creating corresponding account classes
3. Updating the ACCOUNT_CLASSES mapping
4. Adding specific validation logic

## 🤝 Contributing

1. Follow privacy-first design principles
2. Maintain comprehensive test coverage
3. Document all new account types and fields
4. Ensure GDPR compliance for any new personal data

## 📄 License

This project is part of the CraftLore blockchain system for Kashmiri handicraft authentication and supply chain transparency.

---

**Privacy Note**: This Account TP implements privacy-first design where only email addresses are stored as personal data on the blockchain, with all sensitive information managed through secure off-chain services. This ensures GDPR compliance while maintaining the transparency and traceability benefits of blockchain technology.
