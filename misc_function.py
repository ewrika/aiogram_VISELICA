from config import get_admins
from sql import *
from main import bot

# Удаление отступов у текста
def ded(get_text: str):
    if get_text is not None:
        split_text = get_text.split("\n")
        if split_text[0] == "": split_text.pop(0)
        if split_text[-1] == "": split_text.pop(-1)
        save_text = []

        for text in split_text:
            while text.startswith(" "):
                text = text[1:]

            save_text.append(text)
        get_text = "\n".join(save_text)

    return get_text


# Конвертация дней
def convert_day(day):
    day = int(day)
    days = ['день', 'дня', 'дней']

    if day % 10 == 1 and day % 100 != 11:
        count = 0
    elif 2 <= day % 10 <= 4 and (day % 100 < 10 or day % 100 >= 20):
        count = 1
    else:
        count = 2

    return f"{day} {days[count]}"

# Открытие своего профиля
def open_profile_user(user_id):
    get_user = get_userx(user_id=user_id)
    how_days = int(get_unix() - get_user['user_unix']) // 60 // 60 // 24
    return ded(f"""
           <b>👤 Ваш профиль:</b>
           ➖➖➖➖➖➖➖➖➖➖
           🕰 Регистрация: <code>{get_user['user_date'].split(' ')[0]} ({convert_day(how_days)})</code>
           🏆 Рейтинг: <code>{get_user['user_balance']} очков</code>
           🧠 Угадано слов: <code>{get_user['user_win']}</code>
           🦞 Проигрышей: <code>{get_user['user_loose']}</code>
           """)

