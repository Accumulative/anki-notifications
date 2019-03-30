import yaml

class AnkiAccount:

    def __init__(self, trigger, key, anki_user, only_decks = None):
        self.url = 'https://maker.ifttt.com/trigger/{}/with/key/{}'.format(trigger, key)
        self.only_decks = only_decks
        self.collection =  "/etc/anki-sync-server/collections/{}/collection.anki2".format(anki_user)

f = open('config.yml')
config = yaml.safe_load(f)
f.close()

def get_users():
    users = []

    for user in config['users']:
        users.append(AnkiAccount(
            user['ifttt']['event_name'],
            user['ifttt']['key'],
            user['name'],
            user['only_decks']
        ))

    return users