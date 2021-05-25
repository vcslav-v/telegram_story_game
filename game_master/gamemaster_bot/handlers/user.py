from gamemaster_bot import bot
from gamemaster_bot import mem, tools
from gamemaster_bot.menu import tg_user, message, chapter


def extract_link_data(text):
    if len(text.split()) <= 1:
        return
    raw_data = text.split()[1].split('ZZ')
    data = {}
    for item in raw_data:
        key, value = item.split('-')
        data[key] = value
    return data


@bot.message_handler(commands=['start'])
def start_message(msg):
    link_data = extract_link_data(msg.text)
    user = tg_user.TelegramUser(msg.chat.id)
    user_context = mem.UserContext(user.telegram_id)
    user_context.flush_all()
    print(msg.text)
    print(link_data)
    if link_data.get('edit_message_id') and link_data.get('story_id'):
        if int(link_data.get('story_id')) in [story.id for story in user.stories]: 
            _message = message.Message(link_data.get('edit_message_id'))
            user_context.update_context('story_id', link_data.get('story_id'))
            try:
                chapter.Chapter(link_data.get('story_id'), _message.chapter_id)
            except Exception:
                user.show_stories()
                return
            user_context.update_context('chapter_id', _message.chapter_id)
            _message.show(user.telegram_id)
    else:
        user.show_stories()


@bot.callback_query_handler(
    func=tools.is_correct_prefix(tg_user.SHOW_STORIES_PREFIX)
)
def show_user_stories(call):
    user = tg_user.TelegramUser(call.from_user.id)
    user.show_stories()
