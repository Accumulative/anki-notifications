import sqlite3
from sqlite3 import Error
from datetime import datetime
import requests
import random
from . import accounts
# randomly select from most recent 50
limit = 50

class Anki: 

    def __init__(self, db_file):
        self.conn = self.create_connection(db_file)

    def create_connection(self, db_file):
        """ create a database connection to the SQLite database
            specified by the db_file
        :param db_file: database file
        :return: Connection object or None
        """
        try:
            conn = sqlite3.connect(db_file)
            return conn
        except Error as e:
            print(e)

        return None


    def select_cards(self, only_decks, all=False):
        with self.conn:
            cur = self.conn.cursor()
            query = "SELECT flds, due FROM cards left join notes on cards.nid = notes.id where cards.queue=1"
            if only_decks is not None:
                query += " and cards.did in ({})".format(', '.join([str(deck) for deck in only_decks]))

            query += " order by cards.due asc limit {}".format(limit)
            cur.execute(query)

            rows = cur.fetchall()
            if all:
                return list(map(lambda row: list(filter(lambda x: len(x) > 0, row[0].split('\x1f')))[:10], rows))
            else:
                to_send = random.randint(0, len(rows) - 1)
                row = rows[to_send]
                content = list(filter(lambda x: len(x) > 0, row[0].split('\x1f')))[:10]
                return datetime.fromtimestamp(row[1]), content

