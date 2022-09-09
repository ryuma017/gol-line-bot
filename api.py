from linebot import LineBotApi
from linebot.models import (
    TextMessage, TextSendMessage,
)

from constants import CHANNEL_ACCESS_TOKEN

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)

def reply(reply_token, text):
    line_bot_api.reply_message(
        reply_token,
        TextMessage(text=text)
    )

def reply_with_quick_reply_buttons(reply_token, text, quick_reply):
    line_bot_api.reply_message(
        reply_token,
        TextSendMessage(
            text=text,
            quick_reply=quick_reply
        )
    )
