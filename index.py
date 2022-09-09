# Python 3.10.4
# Flask 2.1.2
import logging

from flask import Flask, request, abort
from linebot.exceptions import InvalidSignatureError

import init # Python は import した module は実行されるらしい.
from handlers import handler


app = Flask(__name__)

@app.route("/callback", methods=['POST'])
def index():
    # Get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # Get request body as text
    body = request.get_data(as_text=True)
    logging.info(f"\n\nRequest body: {body}\n\n")

    # Handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        logging.error(
            "Invalid signature. Please check your channel access token/channel secret."
        )
        abort(400) # Raises an HTTPException

    return "", 200 # 200 OK, Content-Length: 0
