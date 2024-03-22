import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.orm import sessionmaker, scoped_session
import json
import datetime as dt

class SqlWrapper:
    def __init__(self, config_file: str):
        """При инициализации сразу настраивает подключение к БД"""
        with open(config_file, 'r') as json_file:
            db_config = json.load(json_file)

        db_url = 'mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}'
        db_url = db_url.format(**db_config)

        self.engine = sqlalchemy.create_engine(db_url, echo=False)
        self.Session = scoped_session(sessionmaker(bind=self.engine))

    def read_data(self, table_name: str) -> pd.DataFrame:
        """Считывает данные таблицы в DataFrame"""
        with self.engine.begin() as conn:
            df = pd.read_sql_table(
                table_name=table_name,
                con=conn
            )

        return df

    def append_data(self, table_name, dataframe: pd.DataFrame | pd.Series):
        """Добавляет данные из DataFrame в таблицу"""
        with self.engine.begin() as conn:
            dataframe.to_sql(name=table_name, if_exists='append', con=conn, index=False)

    def update_data(self, table_name, dataframe: pd.DataFrame | pd.Series):
        """Обновляет существующие данные таблицы"""
        with self.engine.begin() as conn:
            dataframe.to_sql(name=table_name, if_exists='replace', con=conn)

    def execute(self, sql):
        query = sqlalchemy.text(sql)

        with self.engine.connect() as conn:
            result = conn.execute(query)
            conn.commit()

            return result

def get_user_id_of_chat(chat_id: int) -> int:
    """Получает chat_id, а затем выдаёт user_id соответствующего пользователя"""
    df = sqlwrapper.read_data('users')
    df = df[df.chat_id == chat_id]

    if df.shape[0]:
        return df.iloc[0].user_id


def get_current_attempt(user_id: int) -> pd.Series:
    """Возвращает текущую попытку пользвателя <user_id>
    Если её нет - None."""
    df = sqlwrapper.read_data('attempts')
    attempt = df[(df.user_id == user_id)&(df.isna().date_end)]

    return attempt.iloc[0] if attempt.shape[0] else None

def get_current_day_of_attempt(attempt_id: int) -> pd.Series:
    """Возвращает текущий день попытки или None, если его нет"""
    df = sqlwrapper.read_data('days')
    df = df[df.attempt_id == attempt_id].sort_values('relative_pos', ascending=False)

    return df.iloc[0] if df.shape[0] else None

def get_tasks_of_day(day_id: int) -> pd.Series:
    """Возвращает список задач конкретного дня"""
    df = sqlwrapper.read_data('tasks')
    tasks = df[df.day_id == day_id]

    return tasks

def get_task(task_id: int) -> pd.Series | None:
    """Возвращает задачу с id = task_id. Если таковой нет, то None"""
    tasks = sqlwrapper.read_data('tasks')
    task = tasks[tasks.task_id == task_id]

    return task.iloc[0] if task.shape[0] else None

def delete_task(task_id: int) -> None:
    """Удаляет задачу с id = task_id (* Должна существовать !)"""
    sql = f"DELETE FROM tasks WHERE task_id = {task_id}"
    sqlwrapper.execute(sql)

def set_status_task(task_id: int, new_value: int) -> None:
    """Обновляет статус выполнения задачи на new_value"""
    sql = f"UPDATE tasks SET is_completed = {new_value} WHERE task_id = {task_id}"
    sqlwrapper.execute(sql)

def finish_the_attempt(attempt: pd.Series) -> None:
    """Завершает попытку.
    * Если попытка уже является завершённой, то ничего не делает
    * Удаляет исходную запись попытки, если она была начата и удалена в один и тот же день"""
    attempt_id = int(attempt.attempt_id)

    if attempt.isna().date_end:
        date_end = dt.datetime.now().date().isoformat()
        date_beg = attempt.date_beg.to_pydatetime().date().isoformat()

        if date_end == date_beg:
            sql = f"DELETE FROM attempts WHERE attempt_id = {attempt_id}"

        else:
            sql = f"UPDATE attempts SET date_end = '{date_end}' WHERE attempt_id = {attempt_id}"

        sqlwrapper.execute(sql)

def start_new_attempt_of_user(user_id: int) -> None:
    """Начинает новую попытку для пользователя
    * Примечание: Во избежание ошибок, у пользователя не должно быть текущей попытки"""
    # Создаём новую попытку
    data = [[user_id, dt.date.today().isoformat(), np.NaN]]
    sqlwrapper.append_data('attempts', pd.DataFrame(data, columns=['user_id', 'date_beg', 'date_end']))

    # Начинаем первый день
    attempt_id = get_current_attempt(user_id).attempt_id
    start_new_day_of_attempt(attempt_id)

def start_new_day_of_attempt(attempt_id: int) -> None:
    """Создаёт запись нового дня для конкретной попытки"""
    last_day = get_current_day_of_attempt(attempt_id)
    relative_pos = last_day.relative_pos + 1 if last_day else 1
    data = [[attempt_id, relative_pos, np.NaN, np.NaN]]

    sqlwrapper.append_data('days', pd.DataFrame(data, columns=['attempt_id', 'relative_pos', 'total_tasks', 'completed_tasks']))


sqlwrapper = SqlWrapper('mysql_config.json')