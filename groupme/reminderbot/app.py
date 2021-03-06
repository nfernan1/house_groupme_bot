import os
import requests
from flask import Flask, request
from .src.processors.RequestProcessor import RequestProcessor
from .src.controllers.Log import Log

app = Flask(__name__)


@app.route('/')
def index():
    return "Yo, it's working!"


@app.route('/', methods=['POST'])
def webhook():
    data = request.get_json()
    Log.debug('Received {}'.format(data))

    # We don't want to reply to ourselves!
    # if data['name'].lower() != 'reminderbot':
    #     msg = '{}, you sent "{}".'.format(data['name'], data['text'])
    #     send_message(msg)
    rp = RequestProcessor()
    return rp.printRecentMessages(data)


def send_message(msg):
    url = 'https://api.groupme.com/v3/bots/post'

    post_params = {
        'bot_id': os.getenv('BOT_ID'),
        'text': msg,
    }

    botRequest = requests.post(url, post_params)
    msg = "{}".format(botRequest)

if __name__ == "__main__":
    app.run(debug=True, use_reloader=True)