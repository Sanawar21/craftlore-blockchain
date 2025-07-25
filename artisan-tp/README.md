# Artisan Transaction Processor

A Hyperledger Sawtooth transaction processor for managing an artisan marketplace with auto-restart functionality.

## Features

- **Auto-restart**: Automatically restarts when code files change (using watchdog)
- **Artisan Management**: Create and manage artisan profiles
- **Product Listings**: Create and manage product listings
- **Marketplace**: Buy/sell products with transaction tracking
- **Docker Support**: Full containerization with Docker

## Architecture

### Transaction Families
- `artisan`: Artisan profile management
- `product`: Product listing management  
- `transaction`: Purchase transaction records

### Actions Supported
- `create_artisan`: Create an artisan profile
- `create_product`: Create a product listing
- `buy_product`: Purchase a product
- `get_artisan`: Retrieve artisan information
- `get_product`: Retrieve product information

## Files

- `handler.py`: Transaction handler logic
- `processor.py`: Main transaction processor entry point
- `watch.py`: Auto-restart functionality using watchdog
- `client.py`: Test client with demo functionality
- `Dockerfile`: Container configuration
- `requirements.txt`: Python dependencies

## Usage

### Start the Transaction Processor
```bash
docker-compose up -d artisan-tp
```

### View Logs (with auto-restart)
```bash
docker logs -f artisan-tp
```

### Run Test Client
```bash
docker exec artisan-tp python3 client.py
```

### Manual Testing
```bash
# Create artisan
docker exec artisan-tp python3 -c "
from client import ArtisanClient
client = ArtisanClient()
client.create_artisan('art001', 'Master Smith', 'Kashmir', 'Metalwork')
"

# Create product
docker exec artisan-tp python3 -c "
from client import ArtisanClient
client = ArtisanClient()
client.create_product('prod001', 'art001', 'Silver Bowl', 'Handcrafted silver bowl', 150.0, 3)
"
```

## Auto-Restart Feature

The transaction processor includes auto-restart functionality:

- **File Watching**: Monitors all `.py` files for changes
- **Automatic Restart**: Restarts the processor when files are modified
- **Signal Handling**: Graceful shutdown on SIGINT/SIGTERM
- **Logging**: Clear status messages for restarts

### Development Workflow

1. Make changes to any Python file
2. Watch automatically detects changes
3. Processor restarts with new code
4. Test immediately without manual restart

## State Storage

### Artisan Profile
```json
{
  "artisan_id": "artisan001",
  "name": "Master Craftsperson", 
  "location": "Kashmir, India",
  "speciality": "Handwoven Carpets",
  "owner": "03...",
  "created_at": "2025-01-20T10:30:00",
  "products": []
}
```

### Product Listing
```json
{
  "product_id": "product001",
  "artisan_id": "artisan001", 
  "name": "Traditional Carpet",
  "description": "Handwoven carpet with intricate patterns",
  "price": 500.00,
  "quantity": 5,
  "status": "available",
  "created_at": "2025-01-20T10:35:00"
}
```

### Transaction Record
```json
{
  "transaction_id": "txn001",
  "product_id": "product001",
  "artisan_id": "artisan001",
  "buyer": "03...",
  "buyer_info": {"name": "John Doe"},
  "price": 500.00,
  "timestamp": "2025-01-20T10:40:00",
  "status": "completed"
}
```

## Development

The auto-restart feature makes development smooth:

1. Edit `handler.py` to add new functionality
2. The processor automatically restarts
3. Test changes immediately
4. No manual container restarts needed

Perfect for iterative development and testing!
