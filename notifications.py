"""Notification backends for sending Anki card notifications."""

import requests
from abc import ABC, abstractmethod
from typing import Dict, Any
import os


class NotificationBackend(ABC):
    """Abstract base class for notification backends."""

    @abstractmethod
    def send(self, title: str, message: str, data: Dict[str, Any] = None) -> bool:
        """Send a notification."""
        pass


class IFTTTBackend(NotificationBackend):
    """IFTTT webhook notification backend."""

    def __init__(self, event_name: str, key: str):
        self.url = f'https://maker.ifttt.com/trigger/{event_name}/with/key/{key}'

    def send(self, title: str, message: str, data: Dict[str, Any] = None) -> bool:
        """Send notification via IFTTT webhook."""
        try:
            payload = {
                "value1": title,
                "value2": message,
                "value3": data.get('details', '') if data else ''
            }
            response = requests.post(self.url, json=payload, timeout=10)
            return response.status_code == 200
        except requests.RequestException as e:
            print(f"IFTTT notification error: {e}")
            return False


class HomeAssistantBackend(NotificationBackend):
    """Home Assistant notification backend."""

    def __init__(self, url: str, token: str, service: str = 'mobile_app'):
        self.url = url.rstrip('/')
        self.token = token
        self.service = service

    def send(self, title: str, message: str, data: Dict[str, Any] = None) -> bool:
        """Send notification via Home Assistant."""
        try:
            headers = {
                'Authorization': f'Bearer {self.token}',
                'Content-Type': 'application/json'
            }

            payload = {
                "title": title,
                "message": message
            }

            if data:
                payload["data"] = data

            response = requests.post(
                f'{self.url}/api/services/notify/{self.service}',
                headers=headers,
                json=payload,
                timeout=10
            )
            return response.status_code == 200
        except requests.RequestException as e:
            print(f"Home Assistant notification error: {e}")
            return False


class NtfyBackend(NotificationBackend):
    """Ntfy.sh notification backend (self-hosted push notifications)."""

    def __init__(self, url: str, topic: str, token: str = None):
        self.url = url.rstrip('/')
        self.topic = topic
        self.token = token

    def send(self, title: str, message: str, data: Dict[str, Any] = None) -> bool:
        """Send notification via ntfy."""
        try:
            headers = {
                'Title': title,
                'Priority': data.get('priority', 'default') if data else 'default'
            }

            if self.token:
                headers['Authorization'] = f'Bearer {self.token}'

            if data and 'tags' in data:
                headers['Tags'] = ','.join(data['tags'])

            response = requests.post(
                f'{self.url}/{self.topic}',
                headers=headers,
                data=message.encode('utf-8'),
                timeout=10
            )
            return response.status_code == 200
        except requests.RequestException as e:
            print(f"Ntfy notification error: {e}")
            return False


def create_backend(config: Dict[str, Any]) -> NotificationBackend:
    """Factory function to create notification backend from config."""
    backend_type = config.get('type', 'ifttt').lower()

    if backend_type == 'ifttt':
        return IFTTTBackend(
            event_name=config['event_name'],
            key=config['key']
        )
    elif backend_type == 'homeassistant':
        return HomeAssistantBackend(
            url=config['url'],
            token=config['token'],
            service=config.get('service', 'mobile_app')
        )
    elif backend_type == 'ntfy':
        return NtfyBackend(
            url=config['url'],
            topic=config['topic'],
            token=config.get('token')
        )
    else:
        raise ValueError(f"Unknown notification backend: {backend_type}")
