# CraftLore Dashboard

A web-based dashboard for querying and exploring CraftLore blockchain data. This Flask application provides a user-friendly interface to interact with the blockchain via the REST API.

## Features

- **Create Accounts**: Create new blockchain accounts (Supplier, Artisan, Buyer) with type-specific fields
- **Account Queries**: Query accounts by public key or email address
- **Asset Queries**: Look up assets by their ID
- **Transaction Queries**: Retrieve transaction details by signature
- **State Overview**: Browse all blockchain state entries
- **Real-time API Status**: Monitor REST API connectivity
- **Responsive Design**: Works on desktop and mobile devices

## Installation

1. Navigate to the dashboard directory:
```bash
cd craftlore_tp/dashboard
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

Note: You may need to install additional system dependencies for the Sawtooth SDK:
```bash
sudo apt-get update
sudo apt-get install -y python3-dev libssl-dev libffi-dev
```

## Usage

1. Start the dashboard:
```bash
python app.py
```

2. Open your web browser and navigate to:
```
http://localhost:5000
```

3. The dashboard will automatically check the REST API status and display it in the header.

## Configuration

The dashboard connects to the REST API at `http://rest-api:8008` by default. You can modify this by editing the `REST_API_URL` variable in `app.py`.

For local development, you can uncomment the localhost URL:
```python
REST_API_URL = "http://localhost:8008"
```

## API Endpoints

The dashboard provides the following API endpoints:

- `POST /create_account` - Create new blockchain accounts
- `POST /query_account_by_pubkey` - Query account by public key
- `POST /query_account_by_email` - Query account by email
- `POST /query_asset` - Query asset by ID
- `POST /query_transaction` - Query transaction by signature
- `GET /list_all_state` - List all blockchain state entries
- `GET /api_status` - Check REST API status

## File Structure

```
dashboard/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── templates/
│   └── dashboard.html    # Main dashboard template
├── static/               # Static assets (CSS, JS, images)
└── README.md            # This file
```

## Docker Support

To run the dashboard in a Docker container, you can add it to your existing docker-compose.yaml:

```yaml
dashboard:
  build: ./craftlore_tp/dashboard
  ports:
    - "5000:5000"
  depends_on:
    - rest-api
  networks:
    - sawtooth-network
```

## Troubleshooting

1. **API Status shows offline**: Check that the Sawtooth REST API is running and accessible
2. **Connection errors**: Verify the REST_API_URL configuration matches your setup
3. **Import errors**: Ensure you're running from the correct directory and utils are available

## Contributing

This dashboard is part of the CraftLore transaction processor project. Feel free to extend it with additional features or improvements.