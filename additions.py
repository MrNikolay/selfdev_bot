import os
import telebot
from colorama import Fore, Style

def log(message: str, type: int = 1) -> None:
    """
    Функция для вывода информации о работе программы (лог-принты)
    Типы <type>:
        1 - Сообщение о каком-то действии
        2 - Подтверждение успешного выполнения действия
    """
    match type:
        case 1: print(message, end=': ')
        case 2: print(Fore.GREEN + message + Style.RESET_ALL)


def error(message: str, is_wait: bool = True) -> None:
    """Функция для вывода информации о какой-то ошибке"""
    text_error = Fore.RED + message + Style.RESET_ALL
    input(text_error) if is_wait else print(text_error)


def get_token(param_name: str) -> str:
    log('Получаем токен')
    if param_name not in os.environ:
        error('Ошибка: Не удалось найти переменную среды - "TOKEN"', is_wait=False)
        print(
            'Переменная среды с именем "TOKEN" должна содержать токен вашего телеграм-бота.',
            'Установить переменную TOKEN можно так: SET TOKEN=<токен_вашего_бота>', sep='\n'
        )
        exit()

    log('ОК!', type=2)
    return os.environ['TOKEN']


def launch_bot(token: str) -> telebot.TeleBot:
    try:
        log('Инициализируем бот')
        bot = telebot.TeleBot(token)
        log('ОК!', type=2)
        return bot

    except Exception as ex:
        error('Ошибка: При инициализации бота произошла какая-то ошибка', is_wait=False)
        print(ex)
        exit()