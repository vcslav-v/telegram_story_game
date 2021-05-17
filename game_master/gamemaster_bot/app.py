from gamemaster_bot import bot
from gamemaster_bot.handlers import story, chapter, user, message

bot.remove_webhook()
bot.polling()
