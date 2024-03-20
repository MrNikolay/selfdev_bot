import telebot
import parser
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

# Меню редактирования плана
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

def main_menu(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, '', reply_markup=main_menu_markup)


def my_plan(message):
    chat_id = message.chat.id

    try:
        user_id = parser.get_user_id_of_chat(chat_id)
        attempt_id = parser.get_current_attempt(user_id).id
        day = parser.get_current_day_of_attempt(attempt_id)
        tasks = parser.get_tasks_of_day(day.id)

    except:
        bot.send_message(chat_id, 'Ошибка: Вероятно Вам необходимо начать новую попытку!', reply_markup=main_menu_markup)

    mess = f'План на день №{day.relative_pos}\n'

    if tasks.shape[0] == 0:
        mess += '- Вы пока не определили задачи на этот день'

    else:
        tasks.sort_values('is_completed', inplace=True, ascending=False)
        for row_tuple in tasks.iterrows():
            task = row_tuple[1]

            sign = 'ДА' if task.is_completed else 'НЕТ'

            mess += f'{sign} - {task.task_name}'

    mess += f'\nВыполнено: {tasks.is_completed.sum()}/{tasks.shape[1]}'

    bot.send_message(chat_id, mess, reply_markup=plan_menu_markup)

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    is_chat_exists = False  # нужно проверить, общались ли ранее
    if not is_chat_exists:
        mess = f"Привет, {message.from_user.first_name}! Вижу тебя впервые...\n"
        mess += "Я создан для того, чтобы помогать людям быть более продуктивными!\n"
        mess += "Здесь ты можешь составлять план на день, а я буду напоминать тебе о важных задачах и поддерживать на всём пути развития!\n"
        mess += "Итак, ты готов научиться чему-то новому, развить полезную привычку и в целом, стать лучше? Я готов стать твоим спутником.\n\n\n"
        bot.send_message(chat_id, mess, reply_markup=main_menu_markup)
        # + Создай запись пользователя в БД


@bot.message_handler(content_types=['text'])
def general_message_handler(message):
    chat_id = message.chat.id
    delete_previos_messages(message, bot, 2)

    if message.text == 'Мой план':
        my_plan(message)

    elif message.text == ...:
        ...

    else:
        bot.send_message(chat_id, 'Я тебя не понял', reply_markup=main_menu_markup)



print(Fore.RED + '*' + Style.RESET_ALL + ' Бот работает')
bot.polling(non_stop=True)  # P.S: С Богом! ;)