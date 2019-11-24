import accounts
from .anki import Anki
from datetime import datetime
import requests


def make_ifttt_request(url_var, param1, param2, param3):
    requests.post(url_var, {"value1": param1,
                            "value2": param2, "value3": param3})


def main():
    # create a database connection
    for account in accounts.get_users():
        anki = Anki(account.collection)
        date, content = anki.select_cards(account.only_decks)
        make_ifttt_request(account.url, content[0], 'due {}'.format(
            date), ' '.join(content[1:]))

if __name__ == '__main__':
    main()
