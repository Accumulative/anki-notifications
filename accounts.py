import yaml

f = open('config.yml')
config = yaml.safe_load(f)
f.close()

class AnkiAccount:

    def __init__(self, trigger, key, anki_user, only_decks = None):
        self.user = anki_user
        self.url = 'https://maker.ifttt.com/trigger/{}/with/key/{}'.format(trigger, key)
        self.only_decks = only_decks
        self.collection =  "{}/{}/collection.anki2".format(config['anki']['collection_path'], anki_user)

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
