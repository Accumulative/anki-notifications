import sqlite3
from datetime import datetime
import random
from typing import List, Optional, Tuple
from pathlib import Path

# Randomly select from most recent cards
LIMIT = 50

class Anki:
    """Interface for querying Anki database."""

    def __init__(self, db_file: Path):
        self.db_file = db_file
        self.conn = self._create_connection()

    def _create_connection(self) -> Optional[sqlite3.Connection]:
        """Create a database connection to the SQLite database."""
        try:
            # Use read-only URI mode to avoid locking conflicts with anki-sync-server
            uri = f'file:{self.db_file}?mode=ro'
            conn = sqlite3.connect(uri, uri=True, timeout=10.0)
            # Set busy timeout for additional safety
            conn.execute("PRAGMA busy_timeout = 10000")
            return conn
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")
            return None

    def select_cards(self, only_decks: Optional[List[int]] = None,
                    all_cards: bool = False) -> List[List[str]]:
        """
        Select cards from the Anki database.

        Args:
            only_decks: List of deck IDs to filter by
            all_cards: If True, return all cards; if False, return one random card

        Returns:
            List of card fields or tuple of (due_date, card_fields) for single card
        """
        if not self.conn:
            return []

        with self.conn:
            cur = self.conn.cursor()
            query = """
                SELECT flds, due
                FROM cards
                LEFT JOIN notes ON cards.nid = notes.id
                WHERE cards.queue IN (0, 1, 2)
            """

            if only_decks:
                deck_ids = ', '.join(str(deck) for deck in only_decks)
                query += f" AND cards.did IN ({deck_ids})"

            query += f" ORDER BY cards.due ASC LIMIT {LIMIT}"
            cur.execute(query)

            rows = cur.fetchall()
            if not rows:
                return []

            if all_cards:
                return [self._parse_fields(row[0]) for row in rows]
            else:
                random_index = random.randint(0, len(rows) - 1)
                row = rows[random_index]
                return datetime.fromtimestamp(row[1]), self._parse_fields(row[0])

    def _parse_fields(self, fields_str: str) -> List[str]:
        """Parse and clean card fields."""
        return [f for f in fields_str.split('\x1f') if f][:10]

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()

