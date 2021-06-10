from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
import json
import re
from gamemaster_bot import bot
from gamemaster_bot.mem import UserContext
from typing import List


def make_call_back(call_to: str, data: dict = {}):
    return '{call_to}{params}'.format(
        call_to=call_to,
        params=json.dumps(data),
    )


def is_correct_prefix(prefix: str):
    def inner(call):
        user_context = UserContext(call.from_user.id)
        is_wait_user = user_context.get_status == 'wait_line'
        return call.data.startswith(prefix) and not is_wait_user
    return inner


def is_wait_line_for(prefix: str):
    def inner(call):
        user_context = UserContext(call.from_user.id)
        is_wait_user = user_context.get_status() == 'wait_line'
        params = user_context.get_params()
        return params.get('call_to') == prefix and is_wait_user
    return inner


def get_call_back_params(call_data: str):
    call_data = re.sub(r'^.*\?', '', call_data)
    return json.loads(call_data)


def make_inline_keyboard(buttons_rows: List):
    markup = InlineKeyboardMarkup(row_width=8)
    for row in buttons_rows:
        buttons_row = []
        for button in row:
            key, call_data, *tail = button
            if not tail:
                buttons_row.append(InlineKeyboardButton(key, callback_data=call_data))
            else:
                buttons_row.append(InlineKeyboardButton(key, url=tail[0]))
        markup.add(*buttons_row)
    return markup


def send_menu_msg(
    tg_id: int,
    data,
    buttons: List = [],
    row_width=1,
    exit_menu=False,
    content_type='text'
):
    user_context = UserContext(tg_id)
    if user_context.get_status() == 'in_menu' and user_context.get_context('active_menu_msg_id'):
        bot.delete_message(tg_id, user_context.get_context('active_menu_msg_id'))

    if content_type == 'text':
        msg_info = bot.send_message(
            tg_id, data,
            reply_markup=make_inline_keyboard(buttons),
        )
    elif content_type == 'photo':
        msg_info = bot.send_photo(
            tg_id, data['media'],
            caption=data['caption'],
            reply_markup=make_inline_keyboard(buttons),
        )
    elif content_type == 'voice':
        msg_info = bot.send_voice(
            tg_id, data['media'],
            caption=data['caption'],
            reply_markup=make_inline_keyboard(buttons),
        )
    elif content_type == 'video_note':
        msg_info = bot.send_video_note(
            tg_id, data['media'], reply_markup=make_inline_keyboard(buttons)
        )

    user_context.set_status('in_menu')
    user_context.update_context('active_menu_msg_id', msg_info.message_id)
    if exit_menu:
        user_context.rm_context('active_menu_msg_id')
        user_context.rm_status()
