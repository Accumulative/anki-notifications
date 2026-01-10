# Anki Notifications

Flask API and notification service for Anki flashcards. Serves card data via REST API and sends notifications about due cards through various backends.

## Features

- **REST API** - Serves Anki card data for consumption by other apps
- **Multiple Notification Backends**:
  - Home Assistant (recommended for self-hosted)
  - IFTTT (cloud-based webhooks)
  - Ntfy (simple self-hosted push notifications)
- **Flexible Configuration** - Filter by decks, configure per-user settings
- **Production Ready** - Runs with gunicorn, includes health checks
- **Modern Python** - Type hints, proper error handling, clean code

## Quick Start

### With Docker (Recommended)

```bash
# Copy sample config
cp sample_config.yml config.yml

# Edit config.yml with your settings
vim config.yml

# Build and run
docker build -t anki-notifications .
docker run -d \
  -p 5000:5000 \
  -v /path/to/anki/collections:/data/collections:ro \
  -v $(pwd)/config.yml:/app/config.yml:ro \
  anki-notifications
```

### Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure
cp sample_config.yml config.yml
vim config.yml

# Run API server
python api.py

# Or run batch notification script
python batch.py
```

## Configuration

Create `config.yml` from `sample_config.yml`:

```yaml
anki:
  collection_path: /data/collections

users:
  - name: your_username
    notification:
      type: homeassistant
      url: http://your-homeassistant:8123
      token: your_long_lived_access_token
      service: mobile_app
    only_decks: [123456789]  # Optional: filter specific decks
```

### Notification Backend Configuration

#### Home Assistant (Self-Hosted)

Best for self-hosted setups. Requires Home Assistant instance.

```yaml
notification:
  type: homeassistant
  url: http://homeassistant.local:8123
  token: eyJ0eXAiOiJKV1QiLCJhbGc...  # Long-lived access token
  service: mobile_app  # or 'notify' for general notifications
```

Get a token from Home Assistant:
1. Go to Profile → Long-Lived Access Tokens
2. Create new token
3. Copy to config

#### Ntfy (Simple Self-Hosted)

Lightweight push notification service.

```yaml
notification:
  type: ntfy
  url: https://ntfy.sh  # or your self-hosted instance
  topic: anki_cards
  token: optional_auth_token  # Optional
```

#### IFTTT (Cloud)

Legacy support for IFTTT webhooks.

```yaml
notification:
  type: ifttt
  event_name: anki_notification
  key: your_webhook_key
```

## API Endpoints

### `GET /` or `GET /index`

Returns all due cards for all configured users.

**Response:**
```json
{
  "username": [
    ["field1", "field2", "field3"],
    ["word", "definition", "example"]
  ]
}
```

### `GET /health`

Health check endpoint.

**Response:**
```json
{
  "status": "ok"
}
```

## Batch Notifications

Run `batch.py` to send notifications for due cards:

```bash
python batch.py
```

This selects a random due card for each user and sends a notification via the configured backend.

### Scheduling with Cron

```bash
# Send notifications every hour
0 * * * * cd /path/to/anki-notifications && python batch.py
```

### Scheduling with Docker

Use docker-compose to run as a service:

```yaml
services:
  anki-notifier:
    build: .
    volumes:
      - /path/to/collections:/data/collections:ro
      - ./config.yml:/app/config.yml:ro
    command: sh -c "while true; do python batch.py && sleep 3600; done"
```

## Finding Deck IDs

Anki stores deck information in SQLite. To find deck IDs:

```bash
sqlite3 /path/to/collection.anki2
```

```sql
SELECT decks FROM col;
```

Look for deck IDs in the JSON output. Leave `only_decks` as `~` (null) to include all decks.

## Development

### Project Structure

```
anki-notifications/
├── accounts.py       # User account and config management
├── anki.py          # Anki database interface
├── api.py           # Flask API server
├── batch.py         # Batch notification script
├── notifications.py # Notification backend implementations
├── requirements.txt # Python dependencies
├── config.yml       # Configuration (create from sample)
└── Dockerfile       # Docker build configuration
```

### Adding New Notification Backends

1. Create new class extending `NotificationBackend` in `notifications.py`
2. Implement `send()` method
3. Add to `create_backend()` factory function
4. Update `sample_config.yml` with example

Example:

```python
class CustomBackend(NotificationBackend):
    def __init__(self, api_key: str):
        self.api_key = api_key

    def send(self, title: str, message: str, data: Dict[str, Any] = None) -> bool:
        # Your implementation
        return True
```

## Troubleshooting

### Cards not showing up

- Check collection path in `config.yml`
- Verify deck IDs are correct
- Ensure cards are due (queue=1 in database)

### Notifications not sending

- Test notification backend manually
- Check logs for errors
- Verify API keys/tokens are correct
- Ensure network connectivity to notification service

### Database connection errors

- Verify Anki collection path exists
- Check file permissions
- Ensure collection is not locked by Anki

## Requirements

- Python 3.11+
- Flask 3.0+
- Access to Anki sync server collections (or local .anki2 files)
- Notification backend (Home Assistant, Ntfy, or IFTTT)

## License

MIT

## Related Projects

- [anki-scroller](../anki-scroller) - Web UI for displaying cards
- [anki-sync-server](https://github.com/ankicommunity/anki-sync-server) - Self-hosted Anki sync
