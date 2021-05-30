from gamemaster_bot import tools, mem, DB_URL, APP_URL
from gamemaster_bot.menu import chapter
import hashlib

import requests
import json

MAKE_PREFIX = 'make_msg?'
SHOW_PREFIX = 'show_msg?'
RM_PREFIX = 'rm_msg?'
ADD_BUTTON_PREFIX = 'add_btn_msg?'
RM_BUTTON_PREFIX = 'rm_btn_msg?'
EDIT_BUTTON_PREFIX = 'edit_btn_msg?'
EDIT_PREFIX = 'edit_msg?'
ADD_BUTTON_LINK_PREFIX = 'add_btn_link_msg?'
ADD_DIRECT_LINK_PREFIX = 'add_direct_link_msg?'


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


def make_new_msg(tg_id: int, data: dict, content_type: str):
    user_context = mem.UserContext(tg_id)
    params = user_context.get_params()
    from_msg_id = params.get('from_msg_id')
    from_btn_id = params.get('from_btn_id')
    req_data = {
        'tg_id': tg_id,
        'content_type': content_type,
        'message': data.get('message'),
        'story_id': user_context.get_context('story_id'),
        'chapter_id': user_context.get_context('chapter_id'),
        'parrent_message_id': from_msg_id if from_msg_id and not from_btn_id else None,
        'is_start_msg': True if params.get('is_start_chapter_msg') else False,
    }

    new_msg_resp = json.loads(
            requests.post(
                DB_URL.format(item='message', cmd='make'),
                json=req_data,
            ).text
        )
    if content_type == 'photo':
        files = {'file_data': (data['name'], data['photo'], data['content_type'])}
        payload = {
            'tg_id': tg_id,
            'message_id': new_msg_resp.get('id'),
        }
        requests.post(
            DB_URL.format(item='media', cmd='make'),
            files=files,
            data=payload,
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
    _message = Message(new_msg_resp.get('id'))
    _message.show(tg_id)


class Message:
    def __init__(self, message_id: int):
        msg_resp = json.loads(
            requests.post(
                DB_URL.format(item='message', cmd='get'),
                json={'msg_id': message_id},
            ).text
        )
        self.id = int(msg_resp.get('id'))
        self.story_id = msg_resp.get('story_id')
        self.content_type = msg_resp.get('content_type')
        self.is_start_chapter = msg_resp.get('is_start_chapter')
        self.chapter_id = int(msg_resp.get('chapter_id'))
        self.message = msg_resp.get('message')
        self.media = msg_resp.get('media')
        self.link = msg_resp.get('link')
        self.from_buttons = msg_resp.get('from_buttons')
        self.parrent = msg_resp.get('parrent')
        self.buttons = msg_resp.get('buttons')

    def show(self, tg_id: int):
        if self.content_type == 'text':
            data = self.message
        elif self.content_type == 'photo':
            data = {}
            photo = requests.get(
                DB_URL.format(
                    item='media',
                    cmd='get/{item_id}',
                ),
                params={'item_id': hashlib.sha224(bytes(f'{self.media["id"]}{self.id}', 'utf-8')).hexdigest()}
            ).content
            data['photo'] = photo
            data['caption'] = self.message
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
                    ('Delete', tools.make_call_back(RM_BUTTON_PREFIX, {'btn_id': btn['id']})),
                    ('New text', tools.make_call_back(EDIT_BUTTON_PREFIX, {'btn_id': btn['id']})),
                    ('Add link', tools.make_call_back(ADD_BUTTON_LINK_PREFIX, {'btn_id': btn['id']})),
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
            direct_msg_buttons.append(('Prev direct msg', tools.make_call_back(
                SHOW_PREFIX,
                {'msg_id': self.parrent},
            )))

        if not self.buttons:
            if self.link:
                direct_msg_buttons.append(
                    ('Next direct msg', tools.make_call_back(
                        SHOW_PREFIX,
                        {'msg_id': self.link},
                    ))
                )
            else:
                direct_msg_buttons.append(
                    ('Add direct msg', tools.make_call_back(MAKE_PREFIX, {
                        'from_msg_id': self.id,
                    }))
                )
            direct_msg_buttons.append(
                    ('Add direct link', tools.make_call_back(ADD_DIRECT_LINK_PREFIX, {
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
        buttons.append([('Удалить', tools.make_call_back(RM_PREFIX))])
        buttons.append([
            ('К главе', tools.make_call_back(chapter.SHOW_PREFIX)),
            (
                'Все сообщения',
                None,
                '{app_url}chapter/{chapter_uid}'.format(
                    app_url=APP_URL,
                    chapter_uid=hashlib.sha224(bytes(f'{self.chapter_id}{tg_id}', 'utf-8')).hexdigest(),
                )
            ),
        ])

        tools.send_menu_msg(tg_id, data, buttons, content_type=self.content_type)

    def get_new_msg(self, tg_id: int):
        text = 'Новое сообщение:'
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
            self.buttons = rm_btn_msg_resp.get('buttons')
            self.show(tg_id)

    def edit(self, tg_id: int, data: dict, content_type: str):
        req_data = {
            'msg_id': self.id,
            'message': data['message'],
            'content_type': content_type,
            'tg_id': tg_id,
        }
        edit_msg_resp = json.loads(
            requests.post(
                DB_URL.format(item='message', cmd='edit'),
                json=req_data,
            ).text
        )

        if content_type == 'photo':
            files = {'file_data': (data['name'], data['photo'], data['content_type'])}
            payload = {
                'tg_id': tg_id,
                'message_id': self.id,
            }
            requests.post(
                DB_URL.format(item='media', cmd='make'),
                files=files,
                data=payload,
            ).text

        if edit_msg_resp.get('error'):
            msg = edit_msg_resp.get('error')
            tools.send_menu_msg(tg_id, msg)
        else:
            self.message = data['message']
            self.show(tg_id)

    def rm(self, tg_id: int):
        req_data = {
            'msg_id': self.id,
            'tg_id': tg_id,
        }
        rm_msg_resp = json.loads(
            requests.post(
                DB_URL.format(item='message', cmd='rm'),
                json=req_data,
            ).text
        )
        if rm_msg_resp.get('error'):
            msg = rm_msg_resp.get('error')
            tools.send_menu_msg(tg_id, msg)
        else:
            chapter.Chapter(self.story_id, self.chapter_id).show(tg_id)

    def make_sure_rm(self, tg_id: int):
        msg = 'Вы уверены, что хотите удалить это сообщение ?'
        buttons = [
            [('Да', tools.make_call_back(RM_PREFIX, {'is_sure': True}))],
            [('Нет', tools.make_call_back(SHOW_PREFIX))],
        ]
        tools.send_menu_msg(tg_id, msg, buttons)

    def add_direct_link(self, tg_id: int, to_msg_id: str):
        edit_msg_resp = json.loads(
            requests.post(
                DB_URL.format(item='message', cmd='edit'),
                json={
                    'msg_id': self.id,
                    'tg_id': tg_id,
                    'next_message_id': int(to_msg_id),
                },
            ).text
        )
        if edit_msg_resp.get('error'):
            msg = edit_msg_resp.get('error')
            tools.send_menu_msg(tg_id, msg)
        else:
            self.link = int(to_msg_id)
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

    def get_link_btn(self, tg_id: int, btn_id: int):
        text = 'ID сообщения:'
        buttons = [
                [('Назад', tools.make_call_back(SHOW_PREFIX))],
            ]
        tools.send_menu_msg(tg_id, text, buttons)
        user_context = mem.UserContext(tg_id)
        user_context.set_status('wait_line')
        user_context.set_params({'call_to': ADD_BUTTON_LINK_PREFIX, 'btn_id': btn_id})

    def get_direct_link(self, tg_id: int):
        text = 'ID сообщения:'
        buttons = [
                [('Назад', tools.make_call_back(SHOW_PREFIX))],
            ]
        tools.send_menu_msg(tg_id, text, buttons)
        user_context = mem.UserContext(tg_id)
        user_context.set_status('wait_line')
        user_context.set_params({'call_to': ADD_DIRECT_LINK_PREFIX})

    def add_link_btn(self, tg_id: int, next_msg_id: str, btn_id: int):
        edit_btn_msg_resp = json.loads(
            requests.post(
                DB_URL.format(item='message', cmd='edit_button'),
                json={
                    'msg_id': self.id,
                    'tg_id': tg_id,
                    'button_id': btn_id,
                    'link_to_msg_id': int(next_msg_id),
                },
            ).text
        )
        if edit_btn_msg_resp.get('error'):
            msg = edit_btn_msg_resp.get('error')
            tools.send_menu_msg(tg_id, msg)
        else:
            self.buttons = edit_btn_msg_resp.get('buttons')
            self.show(tg_id)        

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
