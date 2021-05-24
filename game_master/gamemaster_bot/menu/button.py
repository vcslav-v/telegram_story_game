from gamemaster_bot import tools, mem, DB_URL
from gamemaster_bot.menu import message

import requests
import json

MAKE_PREFIX = 'make_btn?'
SHOW_PREFIX = 'show_btn?'


def get_new_btn(tg_id: int, is_start_chapter_msg: bool = False):
    text = 'Ответ:'
    buttons = [
            [('Назад', tools.make_call_back(SHOW_PREFIX))],
        ]
    tools.send_menu_msg(tg_id, text, buttons)
    user_context = mem.UserContext(tg_id)
    user_context.set_status('wait_line')
    user_context.set_params({'call_to': MAKE_PREFIX})


def make_new_btn(tg_id: int, msg: str, text: str):
    user_context = mem.UserContext(tg_id)
    new_btn_msg_resp = json.loads(
        requests.post(
            DB_URL.format(item='message', cmd='add_button'),
            json={
                'msg_id': user_context.get_context('message_id'),
                'chapter_id': user_context.get_context('chapter_id'),
                'tg_id': tg_id,
                'text': text,
            },
        ).text
    )
    if new_btn_msg_resp.get('error'):
        msg = new_btn_msg_resp.get('error')
        tools.send_menu_msg(tg_id, msg)
    else:
        _button = Button(
            user_context.get_context('message_id'),
            new_btn_msg_resp.get('buttons')[-1].get('id'),
        )
        _button.show(tg_id)


class Button:
    def __init__(self, message_id: int, button_id: int):
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
