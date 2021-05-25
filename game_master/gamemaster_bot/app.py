from gamemaster_bot import bot, DB_URL, BOT_URL
from gamemaster_bot.handlers import story, chapter, user, message
from flask import Flask
from flask import render_template
import requests
import json

app = Flask(__name__)


@app.route("/<chapter_hash>")
def chapter_map(chapter_hash):
    chapter_map_resp = json.loads(
        requests.post(
            DB_URL.format(item='chapter', cmd='get_chapter_map'),
            json={
                'chapter_hash': chapter_hash,
            },
        ).text
    )
    story_dict = {}
    next_msgs = []
    for msg in chapter_map_resp['messages']:
        if msg['is_start_chapter']:
            next_msgs = [msg['id']]
            writed_msgs = {msg['id']}
        story_dict[msg['id']] = msg
    messages = []
    while len(next_msgs) > 0:
        msg = story_dict[next_msgs.pop()]
        if msg['link']:
            if msg['link'] not in writed_msgs:
                next_msgs.append(msg['link'])
                writed_msgs.add(msg['link'])
        elif msg['buttons']:
            for btn in msg['buttons'][::-1]:
                if btn['next_message_id'] not in writed_msgs and btn['next_message_id']:
                    next_msgs.append(btn['next_message_id'])
                    writed_msgs.add(btn['next_message_id'])
        messages.append(msg)
    return render_template(
        'chapter_template.html',
        story_name=chapter_map_resp['story'],
        chapter_name=chapter_map_resp['name'],
        story_id=chapter_map_resp['story_id'],
        bot_url=BOT_URL,
        messages=messages,
    )


bot.remove_webhook()
bot.polling()
