# CraftLore Asset TP Client Testing Suite

This directory contains comprehensive testing clients for the CraftLore Asset Transaction Processor. These clients allow you to test all functionality of the asset-tp thoroughly.

## 📁 Client Files

### 1. `base_client.py`
**Base functionality for all asset TP operations**
- Transaction creation and submission
- State reading and address generation
- Error handling and response parsing
- Sawtooth connection management

**Key Features:**
- Automatic key pair generation
- Transaction batching and submission
- State address computation
- Response validation

### 2. `asset_creation_client.py`
**Asset creation and initialization testing**
- Create materials, products, work orders, batches
- Initialize asset hierarchies
- Set up supply chain relationships
- Demo scenarios for different asset types

**Asset Types Supported:**
- Materials (raw materials, components)
- Products (finished goods, handmade items)
- Work Orders (production instructions)
- Product Batches (grouped production runs)

### 3. `asset_operations_client.py`
**Asset lifecycle and operations testing**
- Transfer assets between owners
- Lock/unlock assets for processing
- Update asset information
- Manage warranties and certifications
- Handle sustainability data

**Operations Supported:**
- Asset transfers (single and bulk)
- Asset locking/unlocking
- Information updates
- Warranty registration
- Certification management
- Sustainability tracking

### 4. `asset_read_client.py`
**Asset querying and analysis testing**
- Query assets by various criteria
- Analyze supply chain relationships
- Generate reports and statistics
- Monitor asset status and history

**Query Types:**
- Single asset retrieval
- Assets by owner/type/status
- Supply chain analysis
- Asset statistics and reporting

### 5. `comprehensive_test_client.py`
**Complete testing suite combining all functionality**
- Full test suite execution
- Integration testing
- Performance testing
- Error handling validation
- Automated test reporting

## 🚀 Quick Start

### Prerequisites
Make sure you have:
1. Sawtooth network running (validator, REST API, settings TP)
2. Asset TP processor running
3. Required Python packages installed

### Basic Usage

```bash
# Navigate to clients directory
cd asset-tp/clients

# Run comprehensive test suite
python comprehensive_test_client.py full-test

# Run quick functionality test
python comprehensive_test_client.py quick-test

# Test specific functionality
python asset_creation_client.py demo
python asset_operations_client.py demo
python asset_read_client.py demo
```

### Individual Client Usage

#### Asset Creation
```bash
# Create a material
python asset_creation_client.py material SILK_001 silk 100 meters A+ "Kashmir Valley"

# Create a product
python asset_creation_client.py product SHAWL_001 kani_shawl "Hand-woven Kani Shawl" "Premium quality" 299.99 ARTISAN_001

# Create a work order
python asset_creation_client.py work_order WO_001 SHAWL_001 ARTISAN_001 2024-12-31 pattern=traditional size=large

# Run creation demo
python asset_creation_client.py demo
```

#### Asset Operations
```bash
# Transfer an asset
python asset_operations_client.py transfer SHAWL_001 product <new_owner_public_key>

# Lock an asset
python asset_operations_client.py lock SHAWL_001 product "Processing order"

# Update asset information
python asset_operations_client.py update SHAWL_001 product price=349.99 status=completed

# Register warranty
python asset_operations_client.py warranty SHAWL_001 product "CraftLore Warranty" manufacturing 2024-01-01 2026-01-01

# Accept work order (Flow 1) - Only work orders can be accepted
python asset_operations_client.py accept WO_001 work_order

# Run operations demo
python asset_operations_client.py demo
```

#### Asset Reading
```bash
# Get single asset
python asset_read_client.py get SHAWL_001 product

# List assets by owner
python asset_read_client.py by-owner <owner_public_key>

# List assets by type
python asset_read_client.py by-type product

# Analyze supply chain
python asset_read_client.py chain-analysis SHAWL_001 product

# Run reading demo
python asset_read_client.py demo
```

## 🧪 Testing Scenarios

### 1. Creation Testing
Tests all asset creation operations:
- Material creation with various types
- Product creation with different specifications
- Work order creation with artisan assignments
- Batch creation for production runs

### 2. Operations Testing
Tests asset lifecycle management:
- Asset transfers and ownership changes
- Locking/unlocking for processing
- Information updates and modifications
- Warranty and certification management

### 3. Reading Testing
Tests all query operations:
- Single asset retrieval
- Bulk queries by criteria
- Supply chain analysis
- Statistical reporting

### 4. Integration Testing
Tests complex scenarios:
- Complete asset lifecycle (create → update → transfer → work order acceptance)
- Cross-asset relationships
- Multi-step workflows
- Error recovery scenarios

### 5. Performance Testing
Tests system under load:
- Bulk asset creation
- Concurrent operations
- Large query operations
- Response time measurement

### 6. Error Handling Testing
Tests robustness:
- Invalid asset IDs
- Duplicate creation attempts
- Operations on locked assets
- Permission violations

## 📊 Test Reports

The comprehensive test client generates detailed reports showing:
- ✅ Passed tests
- ❌ Failed tests
- ⏱️ Performance metrics
- 📊 Success rates
- 🎯 Overall system health

Example report output:
```
🧪 COMPREHENSIVE TEST REPORT
============================================================

📊 Creation Tests:
  ✅ PASS Material Creation
  ✅ PASS Product Creation
  ✅ PASS Work Order Creation
  ✅ PASS Batch Creation

📊 Operations Tests:
  ✅ PASS Asset Locking
  ✅ PASS Asset Updating
  ✅ PASS Warranty Registration
  ✅ PASS Certification
  ✅ PASS Asset Unlocking

🏁 FINAL RESULTS:
  Total Tests: 25
  Passed: 23
  Failed: 2
  Success Rate: 92.0%
  🎉 EXCELLENT! TP is working great!
```

## 🔧 Configuration

### Environment Variables
```bash
# Sawtooth REST API endpoint (default: http://localhost:8008)
export SAWTOOTH_REST_URL=http://localhost:8008

# Asset TP family name (default: craftlore-asset)
export ASSET_TP_FAMILY=craftlore-asset

# Asset TP version (default: 1.0)
export ASSET_TP_VERSION=1.0
```

### Custom Configuration
Modify the client files to adjust:
- Transaction family settings
- Address generation logic
- Default test data
- Error handling behavior

## 🐛 Troubleshooting

### Common Issues

1. **Connection Errors**
   ```
   Error: Unable to connect to REST API
   ```
   - Check if Sawtooth validator is running
   - Verify REST API endpoint URL
   - Ensure firewall allows connections

2. **Transaction Failures**
   ```
   Error: Transaction failed with status: INVALID
   ```
   - Check asset TP processor logs
   - Verify transaction data format
   - Ensure proper permissions

3. **Asset Not Found**
   ```
   Error: Asset not found
   ```
   - Verify asset ID and type
   - Check if asset was created successfully
   - Ensure proper address generation

4. **Import Errors**
   ```
   ImportError: No module named 'sawtooth_sdk'
   ```
   - Install Sawtooth SDK: `pip install sawtooth-sdk`
   - Check Python environment
   - Verify requirements.txt

### Debug Mode
Enable debug logging by setting:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📚 Additional Resources

- [Sawtooth SDK Documentation](https://sawtooth.hyperledger.org/docs/)
- [CraftLore Asset TP Handler Documentation](../IMPLEMENTATION_SUMMARY.md)
- [Asset TP Architecture Overview](../README.md)

## 🤝 Contributing

To add new test scenarios:
1. Create new test methods in appropriate client files
2. Add command-line interface support
3. Update comprehensive test client
4. Document new functionality in this README

## 📄 License

This testing suite is part of the CraftLore project and follows the same licensing terms.
