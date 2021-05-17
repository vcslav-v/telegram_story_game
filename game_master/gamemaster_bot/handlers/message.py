from gamemaster_bot import bot
from gamemaster_bot import tools, mem
from gamemaster_bot.menu import message


@bot.callback_query_handler(
    func=tools.is_correct_prefix(message.MAKE_PREFIX)
)
def make_msg(call):
    params = tools.get_call_back_params(call.data)
    message.get_new_msg(call.from_user.id, params.get('is_start_chapter_msg'))


@bot.message_handler(
    content_types='text',
    func=tools.is_wait_line_for(message.MAKE_PREFIX),
)
def wait_line_make(msg):
    user_context = mem.UserContext(msg.from_user.id)
    user_context.rm_status()
    message.make_new_msg(msg.from_user.id, msg.text)
