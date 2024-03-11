import telebot
from additions import *

# получаем токен
token = get_token(param_name='TOKEN')

# инициализируем бот
bot = launch_bot(token=token)  # p.s: Дай Бог, чтобы заработало ;)


@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, 'Hello, World!')
    log('Пытаемся не поломаться')
    log('OK!', type=2)


bot.polling(non_stop=True)