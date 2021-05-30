from gamemaster_bot import DB_URL, BOT_URL, app
from flask import render_template
import requests
import json
import hashlib
import base64


@app.route("/chapter/<chapter_hash>")
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
    writed_msgs = set()
    for msg in chapter_map_resp['messages']:
        if msg['is_start_chapter']:
            next_msgs = [msg['id']]
            writed_msgs = {msg['id']}
        story_dict[msg['id']] = msg
    messages = []
    next_chapter_msgs = []
    attach = True
    while len(next_msgs) > 0:
        msgs = []
        for msg_id in next_msgs:
            if msg_id in story_dict.keys():
                msgs.append(story_dict.get(msg_id))
            else:
                next_chapter_msgs.append(json.loads(
                    requests.post(
                        DB_URL.format(item='message', cmd='get'),
                        json={
                            'msg_id': msg_id,
                        },
                    ).text
                ))
                if next_chapter_msgs[-1]['content_type'] != 'text':
                    next_chapter_msgs[-1]['media'] = base64.b64encode(requests.get(
                        DB_URL.format(
                            item='media',
                            cmd='get/{item_id}',
                        ),
                        params={'item_id': hashlib.sha224(bytes(f'{next_chapter_msgs[-1]["media"]["id"]}{next_chapter_msgs[-1]["id"]}', 'utf-8')).hexdigest()}
                    ).content).decode('utf-8')

        next_msgs = []
        for msg in msgs:
            if not msg:
                continue
            if msg['link'] and msg['link'] not in writed_msgs:
                next_msgs.append(msg['link'])
                writed_msgs.add(msg['link'])
            elif msg['buttons']:
                for btn in msg['buttons'][::-1]:
                    if btn['next_message_id'] not in writed_msgs and btn['next_message_id']:
                        next_msgs.append(btn['next_message_id'])
                        writed_msgs.add(btn['next_message_id'])
            if msg['content_type'] != 'text':
                msg['media'] = base64.b64encode(requests.get(
                    DB_URL.format(
                        item='media',
                        cmd='get/{item_id}',
                    ),
                    params={'item_id': hashlib.sha224(bytes(f'{msg["media"]["id"]}{msg["id"]}', 'utf-8')).hexdigest()}
                ).content).decode('utf-8')
            messages.append({'data': msg, 'is_attach': attach})
        if len(next_msgs) == 0:
            attach = False
            unattached_keys = story_dict.keys() - writed_msgs
            for msg_id in unattached_keys:
                msg = story_dict[msg_id]
                if not msg['parrent'] and not msg['from_buttons']:
                    next_msgs.append(msg['id'])
                    writed_msgs.add(msg['id'])
                    break
    return render_template(
        'chapter_template.html',
        story_name=chapter_map_resp['story'],
        chapter_name=chapter_map_resp['name'],
        story_id=chapter_map_resp['story_id'],
        bot_url=BOT_URL,
        messages=messages,
        next_chapter_msgs=next_chapter_msgs,
    )
