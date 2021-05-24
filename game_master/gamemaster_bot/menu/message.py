from gamemaster_bot import tools, mem, DB_URL
from gamemaster_bot.menu import chapter

import requests
import json

MAKE_PREFIX = 'make_msg?'
SHOW_PREFIX = 'show_msg?'
ADD_BUTTON_PREFIX = 'add_btn_msg?'
RM_BUTTON_PREFIX = 'rm_btn_msg?'
EDIT_BUTTON_PREFIX = 'edit_btn_msg?'
EDIT_PREFIX = 'edit_msg?'


def get_new_msg(
    tg_id: int,
    is_start_chapter_msg: bool = False,
    from_msg_id: int = None,
    from_btn_id: int = None,
):
    msg = 'Ваше сообщение:'
    tools.send_menu_msg(tg_id, msg, exit_menu=True)
    user_context = mem.UserContext(tg_id)
    user_context.set_status('wait_line')
    user_context.set_params(
        {
            'call_to': MAKE_PREFIX,
            'is_start_chapter_msg': '1' if is_start_chapter_msg else '',
            'from_msg_id': str(from_msg_id) if from_msg_id else '',
            'from_btn_id': str(from_btn_id) if from_btn_id else '',
        }
    )


def make_new_msg(tg_id: int, msg: str):
    user_context = mem.UserContext(tg_id)
    params = user_context.get_params()
    from_msg_id = params.get('from_msg_id')
    from_btn_id = params.get('from_btn_id')
    new_msg_resp = json.loads(
            requests.post(
                DB_URL.format(item='message', cmd='make'),
                json={
                    'tg_id': tg_id,
                    'story_id': user_context.get_context('story_id'),
                    'chapter_id': user_context.get_context('chapter_id'),
                    'message': msg,
                    'parrent_message_id': from_msg_id if from_msg_id and not from_btn_id else None,
                    'is_start_msg': True if params.get('is_start_chapter_msg') else False,
                },
            ).text
        )
    if from_msg_id and from_btn_id:
        requests.post(
                DB_URL.format(item='message', cmd='edit_button'),
                json={
                    'tg_id': tg_id,
                    'msg_id': from_msg_id,
                    'button_id': from_btn_id,
                    'link_to_msg_id': new_msg_resp.get('id'),
                },
            )
    user_context.flush_params()
    _message = Message(user_context.get_context('chapter_id'), new_msg_resp.get('id'))
    _message.show(tg_id)


class Message:
    def __init__(self, chapter_id: int, message_id: int):
        msg_resp = json.loads(
            requests.post(
                DB_URL.format(item='message', cmd='get'),
                json={'msg_id': message_id},
            ).text
        )
        self.id = int(msg_resp.get('id'))
        self.is_start_chapter = msg_resp.get('is_start_chapter')
        self.chapter_id = int(msg_resp.get('chapter_id'))
        self.message = msg_resp.get('message')
        self.link = msg_resp.get('link')
        self.from_buttons = msg_resp.get('from_buttons')
        self.parrent = msg_resp.get('parrent')
        self.buttons = msg_resp.get('buttons')

    def show(self, tg_id: int):
        text = self.message
        user_context = mem.UserContext(tg_id)
        user_context.rm_status()
        user_context.update_context('message_id', str(self.id))
        buttons = []
        if not self.link:
            for btn in self.buttons:
                if btn['next_message_id']:
                    buttons.append([
                        (f'{btn["text"]} => К сообщению', tools.make_call_back(SHOW_PREFIX, {
                            'msg_id': btn['next_message_id'],
                        }))
                    ])
                else:
                    buttons.append(
                        [
                            (f'{btn["text"]} => Создать сообщение', tools.make_call_back(MAKE_PREFIX, {
                                'from_msg_id': self.id,
                                'from_btn_id': btn['id'],
                            }))
                        ]
                    )
                buttons.append([
                    ('Удалить ответ', tools.make_call_back(RM_BUTTON_PREFIX, {'btn_id': btn['id']})),
                    ('Изменить текст', tools.make_call_back(EDIT_BUTTON_PREFIX, {'btn_id': btn['id']})),
                ])
            buttons.append(
                [
                    ('Добавить ответ', tools.make_call_back(ADD_BUTTON_PREFIX)),
                ]
            )
        buttons.append(
            [
                ('Редактировать', tools.make_call_back(EDIT_PREFIX)),
            ]
        )
        direct_msg_buttons = []
        if self.parrent:
            direct_msg_buttons.append(('Предыдущее связанное сообщение', tools.make_call_back(
                SHOW_PREFIX,
                {'msg_id': self.parrent},
            )))
        
        if not self.buttons:
            if self.link:
                direct_msg_buttons.append(
                    ('Cледующее связанное сообщение', tools.make_call_back(
                        SHOW_PREFIX,
                        {'msg_id': self.link},
                    ))
                )
            else:
                direct_msg_buttons.append(
                    ('Добавить связанное сообшение', tools.make_call_back(MAKE_PREFIX, {
                        'from_msg_id': self.id,
                    }))
                )

        buttons.append(direct_msg_buttons)
        back_from_buttons = []
        if self.from_buttons:
            for from_btn in self.from_buttons:
                back_from_buttons.append((
                    f'<= {from_btn["text"][:8]}',
                    tools.make_call_back(SHOW_PREFIX, {'msg_id': from_btn['parrent_message_id']}),
                ))
        buttons.append(back_from_buttons)
        buttons.append([('К главе', tools.make_call_back(chapter.SHOW_PREFIX))])

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

    def rm_btn(self, tg_id: int, btn_id: int, is_sure: bool = False):
        if not is_sure:
            self.make_sure_rm_btn(tg_id, btn_id)
            return
        else:
            rm_btn_msg_resp = json.loads(
                requests.post(
                    DB_URL.format(item='message', cmd='rm_button'),
                    json={
                        'msg_id': self.id,
                        'tg_id': tg_id,
                        'button_id': btn_id,
                    },
                ).text
            )
        if rm_btn_msg_resp.get('error'):
            msg = rm_btn_msg_resp.get('error')
            tools.send_menu_msg(tg_id, msg)
        else:
            print(rm_btn_msg_resp)
            self.buttons = rm_btn_msg_resp.get('buttons')
            self.show(tg_id)

    def edit(self, tg_id: int, text: str):
        edit_msg_resp = json.loads(
            requests.post(
                DB_URL.format(item='message', cmd='edit'),
                json={
                    'msg_id': self.id,
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

    def get_text_btn(self, tg_id: int, btn_id: int):
        btn = list(btn for btn in self.buttons if btn.get('id') == btn_id)[0]
        text = f'Текущий ответ: {btn["text"]}\n\n Новый ответ:'
        buttons = [
                [('Назад', tools.make_call_back(SHOW_PREFIX))],
            ]
        tools.send_menu_msg(tg_id, text, buttons)
        user_context = mem.UserContext(tg_id)
        user_context.set_status('wait_line')
        user_context.set_params({'call_to': EDIT_BUTTON_PREFIX, 'btn_id': btn_id})

    def edit_text_btn(self, tg_id: int, text: str, btn_id: int):
        edit_btn_msg_resp = json.loads(
            requests.post(
                DB_URL.format(item='message', cmd='edit_button'),
                json={
                    'msg_id': self.id,
                    'tg_id': tg_id,
                    'button_id': btn_id,
                    'text': text,
                },
            ).text
        )
        if edit_btn_msg_resp.get('error'):
            msg = edit_btn_msg_resp.get('error')
            tools.send_menu_msg(tg_id, msg)
        else:
            self.buttons = edit_btn_msg_resp.get('buttons')
            self.show(tg_id)

    def make_sure_rm_btn(self, tg_id: int, btn_id: int):
        btn = list(btn for btn in self.buttons if btn.get('id') == btn_id)[0]
        msg = 'Вы уверены, что хотите удалить ответ "{}"'.format(btn.get('text'))
        buttons = [
            [('Да', tools.make_call_back(RM_BUTTON_PREFIX, {'btn_id': btn_id, 'is_sure': True}))],
            [('Нет', tools.make_call_back(SHOW_PREFIX))],
        ]
        tools.send_menu_msg(tg_id, msg, buttons)
