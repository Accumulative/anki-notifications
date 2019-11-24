from flask import Flask, jsonify
from .anki import Anki
from . import accounts
from flask_cors import CORS
app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes
app.config['JSON_AS_ASCII'] = False

@app.route('/')
@app.route('/index')
def index():
    response = {}
    for account in accounts.get_users():
        anki = Anki(account.collection)
        content = anki.select_cards(account.only_decks, True)
        response[account.user] = content
    return jsonify(response)
