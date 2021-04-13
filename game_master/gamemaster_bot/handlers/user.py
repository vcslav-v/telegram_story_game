from gamemaster_bot import bot
from gamemaster_bot import mem, tools
from gamemaster_bot.menu import tg_user


@bot.message_handler(commands=['start'])
def start_message(message):
    user = tg_user.TelegramUser(message.chat.id)
    user_context = mem.UserContext(user.telegram_id)
    user_context.flush_all()
    user.show_stories()


@bot.callback_query_handler(
    func=tools.is_correct_prefix(tg_user.SHOW_STORIES_PREFIX)
)
def show_user_stories(call):
    user = tg_user.TelegramUser(call.from_user.id)
    user.show_stories()
