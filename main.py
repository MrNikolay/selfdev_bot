import pandas as pd
import telebot
import parser
import const
from telebot import types
from additions import *

token = get_token(param_name='TOKEN')
bot = launch_bot(token=token)

# Главное меню
main_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
btn1 = types.KeyboardButton(const.edit_plan_text)
btn2 = types.KeyboardButton(const.profile_text)
btn3 = types.KeyboardButton(const.reminders_text)
main_markup.row(btn1)
main_markup.row(btn2, btn3)

# Меню редактирования плана
plan_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
btn1 = types.KeyboardButton(const.edit_plan_text)
btn2 = types.KeyboardButton(const.back_main)
plan_markup.row(btn1)
plan_markup.row(btn2)

# Меню профиля
profile_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
btn1 = types.KeyboardButton(const.statistics_text)
btn2 = types.KeyboardButton(const.settings_text)
btn3 = types.KeyboardButton(const.back_main)
profile_markup.row(btn1, btn2)
profile_markup.row(btn3)

# Меню напоминалок
reminder_markup = None  # P.S: ДОДЕЛАТЬ!

# Меню начала новой попытки
start_attempt_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
btn1 = types.KeyboardButton(const.start_attempt_text)
start_attempt_markup.row(btn1)

# Кнопка продолжить
continue_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
btn1 = types.KeyboardButton(const.continue_text)
continue_markup.row(btn1)



def main_menu(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, '', reply_markup=main_markup)


def my_plan(message):
    chat_id = message.chat.id
    print(chat_id)

    user_id = parser.get_user_id_of_chat(chat_id)
    attempt = parser.get_current_attempt(user_id)
    if attempt is None:
        return bot.send_message(chat_id, 'Ошибка: Вероятно, Вам необходимо начать новую попытку!', reply_markup=start_attempt_markup)

    day = parser.get_current_day_of_attempt(attempt.attempt_id)
    tasks = parser.get_tasks_of_day(day.day_id)



    mess = f'План на день №{day.relative_pos}\n\n'

    if tasks.shape[0] == 0:
        mess += '- Вы пока не определили задачи на этот день'

    else:
        tasks.sort_values('is_completed', inplace=True, ascending=False)
        for row_tuple in tasks.iterrows():
            task = row_tuple[1]

            sign = '✅' if task.is_completed else '❌'

            mess += f'{sign} - {task.task_name}\n'

        mess += f'\nВыполнено: {tasks.is_completed.sum()}/{tasks.shape[0]}'

    bot.send_message(chat_id, mess, reply_markup=main_markup)


def edit_plan(message) -> None:
    chat_id = message.chat.id

    user_id = parser.get_user_id_of_chat(chat_id)
    attempt_id = parser.get_current_attempt(user_id).attempt_id
    day_id = parser.get_current_day_of_attempt(attempt_id).day_id
    tasks = parser.get_tasks_of_day(day_id).sort_values('is_completed', ascending=False)

    edit_menu_markup = types.InlineKeyboardMarkup()
    for row_tuple in tasks.iterrows():
        task = row_tuple[1]
        sign = '✅' if task.is_completed else '❌'
        text = f'{sign} - {task.task_name}'
        button = types.InlineKeyboardButton(text, callback_data=f'view_task_{task.task_id}')
        edit_menu_markup.row(button)

    add_text = '+' if tasks.shape[0] else 'Добавить задачу'


    btn1 = types.InlineKeyboardButton(add_text, callback_data='add_task')
    btn2 = types.InlineKeyboardButton('Удалить все задачи', callback_data='delete_all_tasks')
    btn3 = types.InlineKeyboardButton(const.back_main, callback_data='go_back')

    if tasks.shape[0] < 9:
        edit_menu_markup.row(btn1)

    if tasks.shape[0]:
        edit_menu_markup.row(btn2)

    edit_menu_markup.row(btn3)

    mess = 'Редактор задач'

    bot.send_message(chat_id, mess, reply_markup=edit_menu_markup)


def view_task(message, task_id: int) -> None:
    chat_id = message.chat.id
    task = parser.get_task(task_id)

    task_name = task.task_name

    mess = f'Задача: {task_name}\n'
    mess += f'Статус: {'✅' if task.is_completed == 1 else '❌'}'

    if task.is_completed == 1:
        btn1 = types.InlineKeyboardButton('❌ Убрать выполнение', callback_data=f'mark_complete_{task_id}')

    else:
        btn1 = types.InlineKeyboardButton('✅ Выполнено', callback_data=f'mark_complete_{task_id}')

    btn2 = types.InlineKeyboardButton('Изменить текст задачи', callback_data=f'EditText_task_{task_id}')
    btn3 = types.InlineKeyboardButton('🗑 Удалить задачу', callback_data=f'delete_task_{task_id}')
    btn4 = types.InlineKeyboardButton(const.back_main, callback_data='go_back_edit')

    edit_task_markup = types.InlineKeyboardMarkup()
    edit_task_markup.row(btn1)
    edit_task_markup.row(btn2, btn3)
    edit_task_markup.row(btn4)

    bot.edit_message_text(mess, chat_id, message.message_id, reply_markup=edit_task_markup)

def add_task(message) -> None:
    @bot.message_handler(content_types=['text'])
    def message_input_step(message):
        chat_id = message.chat.id
        if message.text == const.back_edit:
            return general_message_handler(message)

        bot.delete_messages(message.chat.id, [message.message_id, message.message_id - 1])
        task_name = message.text

        markup = types.InlineKeyboardMarkup()
        button = types.InlineKeyboardButton(const.back_main, callback_data='go_back_add_task')
        markup.row(button)

        if len(task_name) <= 64:
            user_id = parser.get_user_id_of_chat(message.chat.id)
            attempt_id = parser.get_current_attempt(user_id).attempt_id
            day_id = parser.get_current_day_of_attempt(attempt_id).day_id
            tasks = parser.get_tasks_of_day(day_id)

            if tasks[tasks.task_name == task_name].shape[0] == 0:
                data = [[day_id, task_name, 0]]
                parser.sqlwrapper.append_data('tasks', pd.DataFrame(data, columns=['day_id', 'task_name', 'is_completed']))

                #markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                #button = types.KeyboardButton(const.back_edit)
                #markup.row(button)

                bot.delete_messages(chat_id, [message.message_id, message.message_id - 1])
                edit_plan(message)

            else:
                mess = 'Ошибка: Задача с таким именем уже существует!'
                bot.send_message(chat_id, mess, reply_markup=markup)

        else:
            mess = 'Ошибка: Слишком длинное название для задачи'
            bot.send_message(chat_id, mess, reply_markup=markup)

    chat_id = message.chat.id

    menu_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button = types.KeyboardButton(const.back_edit)
    menu_markup.row(button)

    mess = 'Опишите задачу: '

    msg = bot.send_message(chat_id, mess, reply_markup=menu_markup)
    bot.register_next_step_handler(msg, message_input_step)

def my_profile(message) -> None:
    chat_id = message.chat.id
    ...

def start_attempt(message) -> None:
    """Начинает новую попытку для пользователя"""
    chat_id = message.chat.id
    user_id = parser.get_user_id_of_chat(chat_id)

    current_attempt = parser.get_current_attempt(user_id)
    if current_attempt is not None:  # если попытка имеется
        are_you_sure_markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton('Да', callback_data='start_new_attempt')
        btn2 = types.InlineKeyboardButton('Нет', callback_data='go_back')
        are_you_sure_markup.row(btn1, btn2)

        current_day = parser.get_current_day_of_attempt(current_attempt.attempt_id)
        mess = 'У вас уже есть текущая попытка!\n'
        mess += f'Кол-во пройденных дней: {current_day.relative_pos}\n'
        mess += 'Вы уверены, что хотите начать сначала?'

        bot.send_message(chat_id, mess, reply_markup=are_you_sure_markup)


    else:  # Начинаем новую попытку
        parser.start_new_attempt_of_user(user_id)

        if parser.get_current_attempt(user_id) is not None:  # операция прошла успешно
            mess = 'Вы начали новую попытку\n'
            mess += 'Это означает, что ...\n'
            mess += 'Что-ж, самое время составить план на сегодняшний день!'
            bot.send_message(chat_id, mess, reply_markup=continue_markup)

        else:  # случилась какая-то ошибка
            bot.send_message(chat_id, 'Произошла какая-то ошибка. Попробуйте ещё раз')

def delete_all_tasks(message) -> None:
    chat_id = message.chat.id

    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Да', callback_data='yes_delete_all')
    btn2 = types.InlineKeyboardButton('Нет', callback_data='go_back_edit')
    markup.row(btn1, btn2)

    msg = bot.edit_message_text('Вы уверены, что хотите удалить ВСЕ задачи?', chat_id, message.message_id, reply_markup=markup)


@bot.message_handler(commands=['start'])
def start(message) -> None:
    chat_id = message.chat.id

    if not parser.get_user_id_of_chat(chat_id): # Пользователь не зарегистрирован
        mess = f"Привет, {message.from_user.first_name}! Вижу тебя впервые...\n"
        mess += "Я создан для того, чтобы помогать людям быть более продуктивными!\n"
        mess += "Здесь ты можешь составлять план на день, а я буду напоминать тебе о важных задачах и поддерживать на всём пути развития!\n"
        mess += "Итак, ты готов научиться чему-то новому, развить полезную привычку и в целом, стать лучше? Я готов стать твоим спутником.\n\n\n"
        bot.send_message(chat_id, mess, reply_markup=continue_markup)
        # Регистрация пользователя в БД
        parser.sqlwrapper.append_data('users', pd.DataFrame([[chat_id]], columns=['chat_id']))

    else:
        general_message_handler(message)


@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback) -> None:
    chat_id = callback.message.chat.id
    user_id = parser.get_user_id_of_chat(chat_id)

    if callback.data == 'start_new_attempt':  # Начать новую попытку (нажал "да")
        current_attempt = parser.get_current_attempt(user_id)
        parser.finish_the_attempt(current_attempt)
        start_attempt(callback.message)

    elif callback.data == 'go_back':  # Кнопка "назад"
        msg_id = callback.message.message_id
        bot.delete_message(chat_id, msg_id)
        my_plan(callback.message)

    elif callback.data == 'go_back_edit':
        msg_id = callback.message.message_id
        bot.delete_message(chat_id, msg_id)
        edit_plan(callback.message)

    elif callback.data == 'go_back_add_task':
        msg_id = callback.message.message_id
        bot.delete_message(chat_id, msg_id)
        add_task(callback.message)

    elif 'view_task_' in callback.data:  # Просмотр конкретной задачи
        task_id = int(callback.data.split('_')[2])
        view_task(callback.message, task_id)

    elif 'delete_task_' in callback.data:  # Удаление конкретной задачи
        task_id = int(callback.data.split('_')[2])
        parser.delete_task(task_id)
        bot.delete_message(chat_id, callback.message.message_id)
        edit_plan(callback.message)

    elif 'mark_complete_' in callback.data:  # Изменить статус выполнения задачи
        task_id = int(callback.data.split('_')[2])
        task = parser.get_task(task_id)
        parser.set_status_task(task_id, abs(task.is_completed - 1))
        view_task(callback.message, task_id)

    elif callback.data == 'add_task':  # Добавление новой задачи
        bot.delete_message(chat_id, callback.message.message_id)
        add_task(callback.message)

    elif callback.data == 'delete_all_tasks':  # Удалить сразу все задачи
        delete_all_tasks(callback.message)

    elif callback.data == 'yes_delete_all':
        chat_id = callback.message.chat.id
        user_id = parser.get_user_id_of_chat(chat_id)
        attempt_id = parser.get_current_attempt(user_id).attempt_id
        day_id = parser.get_current_day_of_attempt(attempt_id).day_id
        tasks = parser.get_tasks_of_day(day_id)

        for i, task in tasks.iterrows():
            parser.delete_task(task.task_id)

        markup = types.InlineKeyboardMarkup()
        button = types.InlineKeyboardButton(const.back_edit, callback_data='go_back_edit')
        markup.row(button)

        bot.delete_message(chat_id, callback.message.message_id)
        bot.send_message(chat_id, 'Все задачи были успешно удалены!', reply_markup=markup)

    else:  # для дебагинга (можешь удалить при деплое)
        bot.send_message(chat_id, 'Я не понял callback (функция: callback_message())')


@bot.message_handler(commands=['test'])
def test(message):
    """Функция для тестов ( ПРИ ДЕПЛОЕ УДАЛИТЬ! )"""
    msg = bot.send_message(message.chat.id, 'some text', reply_markup=plan_markup)


@bot.message_handler(content_types=['text'])
def general_message_handler(message):
    chat_id = message.chat.id
    #delete_previos_messages(message, bot, 2)
    bot.delete_messages(chat_id, [message.message_id, message.message_id - 1, message.message_id - 2])

    if message.text == const.edit_plan_text:  # редактировать план
        edit_plan(message) # редактирование плана

    elif message.text == const.profile_text:  # мой профиль
        my_profile(message)

    elif message.text == const.back_main:  # назад в главное меню
        my_plan(message)

    elif message.text == const.back_edit:  # назад в меню редактирования
        edit_plan(message)

    elif message.text == const.start_attempt_text:  # начать новую попытку
        start_attempt(message)

    elif message.text == const.continue_text:  # продолжить
        my_plan(message)

    else:
        bot.send_message(chat_id, 'Ошибка: Вы ввели неизвестную команду', reply_markup=continue_markup)


print(Fore.RED + '*' + Style.RESET_ALL + ' Бот работает')
bot.polling(none_stop=True)  # P.S: С Богом! ;)