from gamemaster_bot import tools, mem, DB_URL

import requests
import json

MAKE_PREFIX = 'make_msg?'


def get_new_msg(tg_id: int, is_start_chapter_msg: bool = False):
    msg = 'Ваше сообщение:'
    tools.send_menu_msg(tg_id, msg, exit_menu=True)
    user_context = mem.UserContext(tg_id)
    user_context.set_status('wait_line')
    user_context.set_params(
        {
            'call_to': MAKE_PREFIX,
            'is_start_chapter_msg': '1' if is_start_chapter_msg else '',
        }
    )


def make_new_msg(tg_id: int, msg: str):
    user_context = mem.UserContext(tg_id)
    params = user_context.get_params()
    new_msg_resp = json.loads(
            requests.post(
                DB_URL.format(item='message', cmd='make'),
                json={
                    'tg_id': tg_id,
                    'story_id': user_context.get_context('story_id'),
                    'chapter_id': user_context.get_context('chapter_id'),
                    'message': msg,
                    'is_start_msg': True if params.get('is_start_chapter_msg') else False
                },
            ).text
        )
    user_context.flush_params()
    _message = Message(user_context.get_context('chapter_id'), new_msg_resp.get('id'))
    _message.show(tg_id)


class Message:
    def __init__(self, chapter_id: int, message_id: int):
        msg_resp = json.loads(
            requests.post(
                DB_URL.format(item='message', cmd='get'),
                json={'chapter_id': chapter_id, 'msg_id': message_id},
            ).text
        )
        self.id = int(msg_resp.get('id'))
        self.is_start_chapter = msg_resp.get('is_start_chapter')
        self.chapter_id = int(msg_resp.get('chapter_id'))
        self.message = msg_resp.get('message')
        self.link = msg_resp.get('link')
        self.parrent = msg_resp.get('parrent')
        self.buttons = msg_resp.get('buttons')

    def show(self, tg_id: int):
        text = self.message
        user_context = mem.UserContext(tg_id)
        user_context.update_context('msg_id', str(self.id))
        tools.send_menu_msg(tg_id, text)
