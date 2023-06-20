import sqlite3
from datetime import datetime
import time
from config import PATH_DATABASE

# Очистка текста от HTML тэгов
def clear_html(get_text):
    if get_text is not None:
        if "<" in get_text: get_text = get_text.replace("<", "*")
        if ">" in get_text: get_text = get_text.replace(">", "*")

    return get_text


# Получение текущего unix времени
def get_unix(full=False):
    if full:
        return time.time_ns()
    else:
        return int(time.time())


# Получение текущей даты
def get_date():
    this_date = datetime.today().replace(microsecond=0)
    this_date = this_date.strftime("%d.%m.%Y %H:%M:%S")

    return this_date

def dict_factory(cursor, row):
    save_dict = {}

    for idx, col in enumerate(cursor.description):
        save_dict[col[0]] = row[idx]

    return save_dict

# Форматирование запроса без аргументов
def update_format(sql, parameters: dict):
    if "XXX" not in sql: sql += " XXX "

    values = ", ".join([
        f"{item} = ?" for item in parameters
    ])
    sql = sql.replace("XXX", values)

    return sql, list(parameters.values())


# Форматирование запроса с аргументами
def update_format_args(sql, parameters: dict):
    sql = f"{sql} WHERE "

    sql += " AND ".join([
        f"{item} = ?" for item in parameters
    ])

    return sql, list(parameters.values())

########################################### ЗАПРОСЫ К БД ###########################################
# Добавление пользователя
def add_userx(user_id, user_login, user_name):
    with sqlite3.connect(PATH_DATABASE) as con:
        con.row_factory = dict_factory
        con.execute("INSERT INTO storage_users "
                    "(user_id, user_login, user_name, user_balance, user_win, user_loose ,user_slovo,user_znach,user_wrong ,user_dlina,user_used,user_date, user_unix) "
                    "VALUES (?, ?, ?, ?, ?, ? ,? , ?, ? ,?,?,? ,?)",
                    [user_id, user_login, user_name, 0, 0, 0, "slovo", "znach", 0,"➖"," ",get_date(), get_unix()])
        con.commit()

# Получение пользователя
def get_userx(**kwargs):
    with sqlite3.connect(PATH_DATABASE) as con:
        con.row_factory = dict_factory
        sql = "SELECT * FROM storage_users"
        sql, parameters = update_format_args(sql, kwargs)
        return con.execute(sql, parameters).fetchone()

# Редактирование пользователя
def update_userx(user_id, **kwargs):
    with sqlite3.connect(PATH_DATABASE) as con:
        con.row_factory = dict_factory
        sql = f"UPDATE storage_users SET"
        sql, parameters = update_format(sql, kwargs)
        parameters.append(user_id)
        con.execute(sql + "WHERE user_id = ?", parameters)
        con.commit()

# Получение настроек
def get_settingsx():
    with sqlite3.connect(PATH_DATABASE) as con:
        con.row_factory = dict_factory
        sql = "SELECT * FROM storage_settings"
        return con.execute(sql).fetchone()

# Изменение слова
def update_slovox(user_id, **kwargs):
    with sqlite3.connect(PATH_DATABASE) as con:
        con.row_factory = dict_factory
        sql = f"UPDATE storage_users SET"
        sql, parameters = update_format(sql, kwargs)
        parameters.append(user_id)
        con.execute(sql + "WHERE user_id = ?", parameters)
        con.commit()

# Получение категории
def get_znachx(**kwargs):
    with sqlite3.connect(PATH_DATABASE) as con:
        con.row_factory = dict_factory
        sql = f"SELECT * FROM storage_users"
        sql, parameters = update_format_args(sql, kwargs)
        return con.execute(sql, parameters).fetchone()

def get_topx(row_size):
    try:
        sqlite_connection = sqlite3.connect(PATH_DATABASE)
        cursor = sqlite_connection.cursor()
        print("Подключен к SQLite")

        sqlite_select_query = """SELECT * from storage_users ORDER BY user_balance DESC"""
        cursor.execute(sqlite_select_query)
        print("Чтение ", row_size, " строк")
        records = cursor.fetchmany(row_size)
        print("Вывод каждой строки \n")
        for row in records:
            print("ID:", row[0])
            print("Имя:", row[1])
            print("Почта:", row[2])
            print("Добавлен:", row[3])
            print("Зарплата:", row[4], end="\n\n")

        cursor.close()

    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
    finally:
        if sqlite_connection:
            sqlite_connection.close()
            print("Соединение с SQLite закрыто")


# Получение всех пользователей
def get_all_usersx():
    with sqlite3.connect(PATH_DATABASE) as con:
        con.row_factory = dict_factory
        sql = "SELECT * FROM storage_users"
        return con.execute(sql).fetchall()







# Создание всех таблиц для БД
def create_dbx():
    with sqlite3.connect(PATH_DATABASE) as con:
        con.row_factory = dict_factory

        # Создание БД с хранением данных пользователей
        if len(con.execute("PRAGMA table_info(storage_users)").fetchall()) == 14:
            print("DB was found(1/8)")
        else:
            con.execute("CREATE TABLE storage_users("
                        "increment INTEGER PRIMARY KEY AUTOINCREMENT,"
                        "user_id INTEGER,"
                        "user_login TEXT,"
                        "user_name TEXT,"
                        "user_balance INTEGER,"
                        "user_win INTEGER,"
                        "user_loose INTEGER,"
                        "user_slovo TEXT,"
                        "user_znach TEXT,"
                        "user_wrong INTEGER,"
                        "user_dlina TEXT,"
                        "user_used TEXT,"
                        "user_date TIMESTAMP,"
                        "user_unix INTEGER)")
            print("DB was not found(1/8) | Creating...")

        # Создание БД с хранением настроек
        if len(con.execute("PRAGMA table_info(storage_settings)").fetchall()) == 9:
            print("DB was found(3/8)")
        else:
            con.execute("CREATE TABLE storage_settings("
                        "status_work TEXT,"
                        "status_refill TEXT,"
                        "status_buy TEXT,"
                        "misc_faq TEXT,"
                        "misc_support TEXT,"
                        "misc_bot TEXT,"
                        "misc_update TEXT,"
                        "misc_profit_day INTEGER,"
                        "misc_profit_week INTEGER)")

            con.execute("INSERT INTO storage_settings("
                        "status_work, status_refill, status_buy, misc_faq, misc_support,"
                        "misc_bot, misc_update, misc_profit_day, misc_profit_week)"
                        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        ["True", "False", "False", "None", "None", "None", "False", get_unix(), get_unix()])
            print("DB was not found(3/8) | Creating...")



        con.commit()