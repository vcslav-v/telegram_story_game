from gamemaster_bot import bot
from gamemaster_bot import tools, mem
from gamemaster_bot.menu import message


@bot.callback_query_handler(
    func=tools.is_correct_prefix(message.MAKE_PREFIX)
)
def make_msg(call):
    params = tools.get_call_back_params(call.data)
    message.get_new_msg(call.from_user.id, params.get('is_start_chapter_msg'))


@bot.callback_query_handler(
    func=tools.is_correct_prefix(message.SHOW_PREFIX)
)
def show_msg(call):
    user_context = mem.UserContext(call.from_user.id)
    _message = message.Message(
        user_context.get_context('chapter_id'),
        user_context.get_context('message_id'),
        )
    _message.show(call.from_user.id)


@bot.callback_query_handler(
    func=tools.is_correct_prefix(message.EDIT_PREFIX)
)
def edit_msg(call):
    user_context = mem.UserContext(call.from_user.id)
    _message = message.Message(
        user_context.get_context('chapter_id'),
        user_context.get_context('message_id'),
        )
    _message.get_new_msg(call.from_user.id)


@bot.message_handler(
    content_types='text',
    func=tools.is_wait_line_for(message.MAKE_PREFIX),
)
def wait_line_make(msg):
    user_context = mem.UserContext(msg.from_user.id)
    user_context.rm_status()
    message.make_new_msg(msg.from_user.id, msg.text)


@bot.message_handler(
    content_types='text',
    func=tools.is_wait_line_for(message.EDIT_PREFIX),
)
def wait_line_edit(msg):
    user_context = mem.UserContext(msg.from_user.id)
    user_context.rm_status()
    _message = message.Message(
        user_context.get_context('chapter_id'),
        user_context.get_context('message_id'),
        )
    _message.edit(msg.from_user.id, msg.text)