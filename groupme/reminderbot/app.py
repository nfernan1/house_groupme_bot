import sys

import os
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from flask import Flask, request

app = Flask(__name__)

@app.route('/')
def index():
    return "Yo, it's working!"

@app.route('/', methods=['POST'])
def webhook():
    data = request.get_json()
    log('Received {}'.format(data))

    # We don't want to reply to ourselves!
    if data['name'].lower() != 'reminderbot':
        msg = '{}, you sent "{}".'.format(data['name'], data['text'])
        send_message(msg)

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

# def main():
#     rp = RequestProcessor()
#     rp.printRecentMessages()
#
#     print("Hello World")
#
#
# if __name__ == "__main__":
#     main()
