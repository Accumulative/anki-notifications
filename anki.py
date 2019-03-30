import sqlite3
from sqlite3 import Error
from datetime import datetime
import requests
import random
import accounts
# randomly select from most recent 50
limit = 50


def create_connection(db_file):
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


def select_cards(conn, url, only_decks):
    cur = conn.cursor()
    query = "SELECT flds, due FROM cards left join notes on cards.nid = notes.id where cards.queue=1"
    if only_decks is not None:
        query += " and cards.did in ({})".format(', '.join([str(deck) for deck in only_decks]))

    query += " order by cards.due asc limit {}".format(limit)
    cur.execute(query)

    rows = cur.fetchall()
    to_send = random.randint(0, len(rows) - 1)
    row = rows[to_send]
    content = filter(lambda x: len(x) > 0, row[0].split('\x1f'))[:10]
    make_ifttt_request(url, content[0], 'due {}'.format(datetime.fromtimestamp(row[1])), ' '.join(content[1:]))


def main():
    # create a database connection
    for account in accounts.get_users():
        print(account.collection)
        conn = create_connection(account.collection)
        with conn:
            select_cards(conn, account.url, account.only_decks)


def make_ifttt_request(url_var, param1, param2, param3):
    requests.post(url_var, {"value1": param1, "value2": param2, "value3": param3})


if __name__ == '__main__':
    main()
