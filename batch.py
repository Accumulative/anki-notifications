"""Batch script to send Anki card notifications."""

from accounts import get_users
from anki import Anki
import re


def clean_html(text):
    """Remove HTML tags and clean up text."""
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Remove extra whitespace
    text = ' '.join(text.split())
    return text


def extract_meaning(content):
    """Extract a clean meaning from card content, including reading."""
    # Based on your card structure:
    # content[0] = Japanese word
    # content[1] = Reading with furigana
    # content[2] = English definition/meaning
    # content[3] = Plain reading

    if len(content) > 2:
        # Get the reading and definition
        reading = clean_html(content[1]) if len(content) > 1 else ''
        meaning = clean_html(content[2])

        # Combine reading and meaning
        if reading:
            combined = f"{reading} - {meaning}"
        else:
            combined = meaning

        # Take first ~150 chars for notification
        if len(combined) > 150:
            combined = combined[:147] + '...'
        return combined
    elif len(content) > 1:
        # Fallback to reading
        return clean_html(content[1])
    return "Review this card"


def main():
    """Send notifications for due cards to all configured users."""
    for account in get_users():
        try:
            anki = Anki(account.collection)
            date, content = anki.select_cards(account.only_decks, all_cards=False)

            if not content:
                print(f"No cards found for user {account.user}")
                continue

            # Send notification
            title = content[0] if content else "Anki Card Due"
            message = extract_meaning(content)
            # Include reading in details if available
            reading = content[1] if len(content) > 1 else ''

            success = account.send_notification(
                title=title,
                message=message,
                data={'reading': clean_html(reading) if reading else ''}
            )

            if success:
                print(f"Notification sent for user {account.user}")
            else:
                print(f"Failed to send notification for user {account.user}")

            anki.close()

        except Exception as e:
            print(f"Error processing user {account.user}: {e}")


if __name__ == '__main__':
    main()
