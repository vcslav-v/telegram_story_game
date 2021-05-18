from gamemaster_bot import tools, mem, DB_URL
from gamemaster_bot.menu import chapter

import requests
import json

MAKE_PREFIX = 'make_msg?'
SHOW_PREFIX = 'show_msg?'
ADD_BUTTON_PREFIX = 'add_btn_msg?'
SHOW_BUTTON_PREFIX = 'show_btn_msg?'
EDIT_PREFIX = 'edit_msg?'


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
        pass

    def show(self, tg_id: int):
        text = self.message
        user_context = mem.UserContext(tg_id)
        user_context.rm_status()
        user_context.update_context('message_id', str(self.id))
        buttons = []
        for btn in self.buttons:
            buttons.append([(btn['text'], tools.make_call_back(ADD_BUTTON_PREFIX))])
        buttons.extend([
            [
                ('Добавить ответ', tools.make_call_back(ADD_BUTTON_PREFIX)),
            ],
            [
                ('Редактировать', tools.make_call_back(EDIT_PREFIX)),
                ('К главе', tools.make_call_back(chapter.SHOW_PREFIX))
            ],
        ])
        tools.send_menu_msg(tg_id, text, buttons)

    def get_new_msg(self, tg_id: int):
        text = f'Прошлое сообщение:\n{self.message}\n\nНовый вариант:'
        buttons = [
                [('Назад', tools.make_call_back(SHOW_PREFIX))],
            ]
        tools.send_menu_msg(tg_id, text, buttons)
        user_context = mem.UserContext(tg_id)
        user_context.set_status('wait_line')
        user_context.set_params({'call_to': EDIT_PREFIX})

    def get_new_btn(self, tg_id: int):
        text = 'Ответ:'
        buttons = [
                [('Назад', tools.make_call_back(SHOW_PREFIX))],
            ]
        tools.send_menu_msg(tg_id, text, buttons)
        user_context = mem.UserContext(tg_id)
        user_context.set_status('wait_line')
        user_context.set_params({'call_to': ADD_BUTTON_PREFIX})

    def add_button(self, tg_id: int, text: str):
        new_btn_msg_resp = json.loads(
            requests.post(
                DB_URL.format(item='message', cmd='add_button'),
                json={
                    'msg_id': self.id,
                    'chapter_id': self.chapter_id,
                    'tg_id': tg_id,
                    'text': text,
                },
            ).text
        )
        if new_btn_msg_resp.get('error'):
            msg = new_btn_msg_resp.get('error')
            tools.send_menu_msg(tg_id, msg)
        else:
            self.buttons.append(new_btn_msg_resp['buttons'][-1])
            self.show(tg_id)

    def edit(self, tg_id: int, text: str):
        edit_msg_resp = json.loads(
            requests.post(
                DB_URL.format(item='message', cmd='edit'),
                json={
                    'msg_id': self.id,
                    'chapter_id': self.chapter_id,
                    'tg_id': tg_id,
                    'message': text,
                },
            ).text
        )
        if edit_msg_resp.get('error'):
            msg = edit_msg_resp.get('error')
            tools.send_menu_msg(tg_id, msg)
        else:
            self.message = text
            self.show(tg_id)
