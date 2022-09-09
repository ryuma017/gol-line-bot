import logging
import os
import subprocess
import random

from linebot import WebhookHandler
from linebot.models import (
    QuickReply, QuickReplyButton, PostbackAction
)
from linebot.models.events import (
    FollowEvent, MessageEvent, PostbackEvent,
)

from constants import (
    CHANNEL_SECRET, GIT_REPOSITORY_ROOT_PATH, NETLIFY_APP_URL,
)
from errors import InvalidCellState, InvalidField, InvalidHeightField, InvalidLiteral, InvalidWidthField
from logic import gen_random_field, gen_and_save_gif_to_repository
from api import reply, reply_with_quick_reply_buttons


handler = WebhookHandler(CHANNEL_SECRET)

@handler.add(MessageEvent)
def message_event_handler(event):
    reply_token = event.reply_token
    user_id = event.source.user_id
    lines = event.message.text.strip().split("\n")

    if lines[0] in ["PRAY", "pray", "Pray"]:
        reply(
            reply_token,
            "祈ラナイで",
        )

    if (len(lines) == 1) and (lines[0] in ["PLAY", "play", "プレイ", "ぷれい"]):
        reply_with_quick_reply_buttons(
            reply_token,
            "遊び方を選んでください",
            QuickReply([
                QuickReplyButton(action=PostbackAction(label="手動入力", data="manual")),
                QuickReplyButton(action=PostbackAction(label="ランダム生成", data="random")),
            ]),
        )
        return
    
    if len(lines) == 1:
        try:
            width, height, random_field = gen_random_field(lines)

        except InvalidLiteral as e:
            logging.error(e)
            reply(
                reply_token,
                random.choice([
                    "https://github.com/ryuma017",
                    "https://twitter.com/ryuma017",
                    "https://qiita.com/ryuma017"
                ])
            )
            return

        else:
            logging.info(f"\n\n{random_field}\n\n")
            reply(
                reply_token,
                f"{width} {height}\n{random_field}"
            )
            return

    try:
        gen_and_save_gif_to_repository(lines, user_id)

    except InvalidField as e:
        logging.error(e)
        reply(
            reply_token,
            """\
無効な入力です.

[エラー]
・width と 長さが一致しない行があります.
・height と field の行数が一致しません\
"""
        )
        return

    except InvalidWidthField as e:
        logging.error(e)
        reply(
            reply_token,
            """\
無効な入力です.

[エラー]
・width と 長さが一致しない行があります.\
"""
        )
        return

    except InvalidHeightField as e:
        logging.error(e)
        reply(
            reply_token,
            """\
無効な入力です.

[エラー]
・height と field の行数が一致しません.\
"""
        )
        return
    
    except InvalidCellState as e:
        logging.error(e)
        reply(
            reply_token,
            """\
無効な入力です.

・field に 0, 1 以外の文字が含まれています.\
"""
        )
        return

    # TODO: 切り出す
    os.chdir(GIT_REPOSITORY_ROOT_PATH)
    cd = os.getcwd()
    subprocess.run(["git add ."], check=True, shell=True)
    commit_msg = f"add {user_id}.gif"
    try:
        subprocess.run([f"git commit -m '{commit_msg}'"], check=True, shell=True)
    
    # 前回と同じ field が送信された場合
    except subprocess.CalledProcessError:
        reply(
            reply_token,
            f"""\
GIF URL:
{NETLIFY_APP_URL}/users/{user_id}.gif

前回と同じです.\
"""
        )

    else:
        subprocess.run(["git push origin main"], check=True, shell=True)
        logging.info("deploy")

        reply(
            reply_token,
            f"""\
GIF URL:
{NETLIFY_APP_URL}/users/{user_id}.gif

GIF が反映されるのには数秒かかります.
また、前回の結果は上書きされます.\
"""
        )

@handler.add(FollowEvent)
def join_event_handler(event):
    reply(
        event.reply_token,
        "Life Game Bot へようこそ.\n`play` と入力すると始まります.",
    )

@handler.add(PostbackEvent)
def postback_event_handler(event):
    reply_token = event.reply_token
    data = event.postback.data
    match data:
        case "manual":
            reply(
                reply_token,
                """\
**手動入力**

次の形式に従って入力してください.

width は field の横幅.
height は field の縦幅.
0, 1 はそれぞれ cell の state (Alive, Dead) を表します.

[1行目]
width, height を 半角数字 を使って 空白区切り で入力.

例:
```
5 5
```

[2行目以降]
1行目に入力した制約に対応するように、改行区切りで半角数字の 0 と 1 を入力します.

例:
```
5 5
00000
00100
00010
01110
00000
```\
"""
            )

        case "random":
            reply(
                reply_token,
                """\
**ランダム生成**

width, height を 半角数字 を使って 空白区切り で 1行 で入力してください.

入力に対応する field が返されるので、全てコピーして送り返してください.

width * height は5000より小さい必要があります.

例:
```
50 50
```\
"""
            )
