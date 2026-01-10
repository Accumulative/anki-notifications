"""Flask API for serving Anki card data."""

from flask import Flask, jsonify
from flask_cors import CORS
from accounts import get_users
from anki import Anki
import os

app = Flask(__name__)
CORS(app)
app.config['JSON_AS_ASCII'] = False


@app.route('/')
@app.route('/index')
def index():
    """Return all due cards for all users."""
    response = {}

    for account in get_users():
        try:
            anki = Anki(account.collection)
            content = anki.select_cards(account.only_decks, all_cards=True)
            response[account.user] = content
            anki.close()
        except Exception as e:
            print(f"Error fetching cards for {account.user}: {e}")
            response[account.user] = []

    return jsonify(response)


@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok"})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)
