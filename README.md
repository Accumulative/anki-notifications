# How to use this repository
```
git clone https://github.com/Accumulative/anki-notifications
cd anki-notifications
virtualenv env
source env/bin/activate
pip install -r requirements.txt
```
Then create a config.yml by copying the sample and changing the values

# About the program
- it assumes you have your own anki server, the setup of which can be found
here: [anki-sync-server](https://github.com/dsnopek/anki-sync-server)
- it assumes you have set up an ifttt account which has an applet 
configured with the input being a webhook and the output being the 
notification platform of your choice (I use Line)
- it sends the word, the due date and the rest of the details in the 
field 1, field 2 and field 3 respectively
- if you wish to change the api used, it would only be a small change

# About the config
- the name field is the name of the collection (or the username that is used)
to log in
- the only_decks field is to filter out which decks you want notifications to 
be sent from. the decks can be found out by running the follow sql in the 
collection sqlite3 database
```
SELECT decks FROM col;
```
- as used in the program, the sqlite3 for anki-sync-server can be found at:
/etc/anki-sync-server/collections/{user_name}/collection.anki2