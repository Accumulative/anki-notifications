import yaml
from pathlib import Path
from typing import List, Optional
from notifications import create_backend, NotificationBackend

def load_config(config_path: str = 'config.yml') -> dict:
    """Load configuration from YAML file."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

class AnkiAccount:
    """Represents an Anki account with notification backend."""

    def __init__(self, anki_user: str, collection_path: str,
                 notification_config: dict, only_decks: Optional[List[int]] = None):
        self.user = anki_user
        self.only_decks = only_decks
        self.collection = Path(collection_path) / anki_user / 'collection.anki2'
        self.notifier = create_backend(notification_config)

    def send_notification(self, title: str, message: str, data: dict = None) -> bool:
        """Send a notification using the configured backend."""
        return self.notifier.send(title, message, data)

def get_users(config_path: str = 'config.yml') -> List[AnkiAccount]:
    """Load user accounts from configuration file."""
    config = load_config(config_path)
    users = []

    collection_path = config['anki']['collection_path']

    for user in config['users']:
        # Support both old IFTTT config and new notification config
        if 'notification' in user:
            notification_config = user['notification']
        elif 'ifttt' in user:
            # Backward compatibility with old IFTTT config
            notification_config = {
                'type': 'ifttt',
                'event_name': user['ifttt']['event_name'],
                'key': user['ifttt']['key']
            }
        else:
            raise ValueError(f"User {user['name']} missing notification configuration")

        users.append(AnkiAccount(
            anki_user=user['name'],
            collection_path=collection_path,
            notification_config=notification_config,
            only_decks=user.get('only_decks')
        ))

    return users
