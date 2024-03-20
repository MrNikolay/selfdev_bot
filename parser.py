import pandas as pd
import sqlalchemy
import json

class SqlWrapper:
    def __init__(self, config_file: str):
        """При инициализации сразу настраивает подключение к БД"""

        with open(config_file, 'r') as json_file:
            db_config = json.load(json_file)

        db_url = 'mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}'
        db_url = db_url.format(**db_config)

        self.engine = sqlalchemy.create_engine(db_url, echo=False)

    def read_data(self, table_name: str):
        """Считывает данные таблицы в DataFrame"""

        with self.engine.begin() as conn:
            df = pd.read_sql_table(
                table_name=table_name,
                con=conn
            )

        return df

    def append_data(self, table_name, dataframe: pd.DataFrame):
        """Добавляет данные из DataFrame в таблицу"""

        with self.engine.begin() as conn:
            dataframe.to_sql(name=table_name, if_exists='append', con=conn, index=False)


def get_user_id_of_chat(chat_id: int) -> int:
    df = sqlwrapper.read_data('users')
    user_id = df[df.chat_id == chat_id].iloc[0].user_id

    return user_id

def get_current_attempt(user_id: int) -> pd.Series:
    df = sqlwrapper.read_data('attempts')
    attempt = df[(df.user_id == user_id)&(df.isna().date_end)]

    if attempt.shape[1] == 0:
        raise Exception('У пользователя нет текущей попытки!')

    return attempt

def get_current_day_of_attempt(attempt_id: int) -> pd.Series:
    df = sqlwrapper.read_data('days')
    day = df[df.attempt_id == attempt_id].sort_values('relative_pos', ascending=False).iloc[0]

    return day

def get_tasks_of_day(day_id: int) -> pd.Series:
    df = sqlwrapper.read_data('tasks')
    tasks = df[df.day_id == day_id]

    return tasks


sqlwrapper = SqlWrapper('mysql_config.json')
