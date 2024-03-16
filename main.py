import telebot
from telebot import types
from additions import *

token = get_token(param_name='TOKEN')
bot = launch_bot(token=token)

# Главное меню
main_menu_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
btn1 = types.KeyboardButton('Мой план')
btn2 = types.KeyboardButton('Профиль')
btn3 = types.KeyboardButton('Напоминалки')
main_menu_markup.row(btn1)
main_menu_markup.row(btn2, btn3)

# Меню составления плана
plan_menu_markup = None  # P.S: ДОДЕЛАТЬ!

# Меню профиля
profile_menu_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
btn1 = types.KeyboardButton('Статистика')
btn2 = types.KeyboardButton('Настройки')
btn3 = types.KeyboardButton('Назад')
profile_menu_markup.row(btn1, btn2)
profile_menu_markup.row(btn3)

# Меню напоминалок
reminder_menu_markup = None  # P.S: ДОДЕЛАТЬ!


@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    is_chat_exists = False  # нужно проверить, общались ли ранее
    if not is_chat_exists:
        mess = f"Привет, {message.from_user.first_name}! Вижу тебя впервые...\n"
        mess += "Я создан для того, чтобы помогать людям быть более продуктивными!\n"
        mess += "Здесь ты можешь составлять план на день, а я буду напоминать тебе о важных задачах и поддерживать на всём пути развития!\n"
        mess += "Итак, ты готов научиться чему-то новому, развить полезную привычку и в целом, стать лучше? Я готов стать твоим спутником.\n\n\n"
        bot.send_message(chat_id, mess)

@bot.message_handler(content_types=['text'])
def general_message_handler(message):
    chat_id = message.chat.id
    mess_id = message.message_id

    bot.delete_message(chat_id, mess_id - 1)
    bot.send_message(chat_id, 'Бла бла бла', reply_markup=main_menu_markup)
    bot.delete_message(chat_id, mess_id - 2)

print(Fore.RED + '*' + Style.RESET_ALL + ' Бот работает')
bot.polling(non_stop=True)  # P.S: С Богом! ;)