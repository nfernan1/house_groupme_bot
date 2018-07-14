import os
import sys
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from flask import Flask, request

from .src.processors.RequestProcessor import RequestProcessor

app = Flask(__name__)

@app.route('/')
def index():
    return "Yo, it's working!"

@app.route('/', methods=['POST'])
def webhook():
    data = request.get_json()
    log('Received {}'.format(data))
    rp = RequestProcessor()
    rp.printRecentMessages()

    # # We don't want to reply to ourselves!
    # if data['name'].lower() != 'reminderbot':
    #     msg = '{}, you sent "{}".'.format(data['name'], data['text'])
    #     send_message(msg)

    return "ok", 200


def send_message(msg):
    url = 'https://api.groupme.com/v3/bots/post'

    data = {
        'bot_id': os.getenv('BOT_ID'),
        'text': msg,
    }
    botRequest = Request(url, urlencode(data).encode())
    jsonResponse = urlopen(botRequest).read().decode()


def log(msg):
    print(str(msg))
    sys.stdout.flush()


if __name__ == "__main__":
    app.run(debug=True, use_reloader=True)