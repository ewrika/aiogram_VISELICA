import asyncio
from contextlib import suppress
from aiogram import types
from aiogram.types import Message, CallbackQuery, ContentType
from aiogram.dispatcher.filters import Text, Command, BoundFilter
from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.exceptions import MessageNotModified, CantParseEntities

from LittlebitWords import rand
from config import get_admins, PATH_DATABASE
from inline import mail_confirm_inl
from main import bot,dp,chat_id
from aiogram.dispatcher import  FSMContext
from misc_function import open_profile_user
from sql import *


global loose
global win
global podz
podz = -2
win = 5
loose = -3
HANGMAN = (
    """
     ------
     |    |
     |
     |
     |
     |
     |
    ----------
    """,
    """
     ------
     |    |
     |    😇
     |
     |
     |
     |
    ----------
    """,
    """
     ------
     |    |
     |    🙁
     |    |
     | 
     |   
     |    
    ----------
    """,
    """
     ------
     |    |
     |    🥺
     |   /|
     |   
     |   
     |   
    ----------
    """,
    """
     ------
     |    |
     |    😫
     |   /|\\
     |   
     |   
     |     
    ----------
    """,
    """
     ------
     |    |
     |    😩
     |   /|\\
     |   /
     |   
     |    
    ----------
    """,
    """
     ------
     |    |
     |    ☠
     |   /|\\
     |   / \\
     |   
     |   
    ----------
    """
)

used=[]
global wrong
wrong = 0
db=PATH_DATABASE
max_wrong = len(HANGMAN) - 1
# Проверка на админа

class IsAdmin(BoundFilter):
    async def check(self, message: types.Message):
        if message.from_user.id in get_admins():
            return True
        else:
            return False

# Кнопки главного меню
def menu_frep(user_id):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row("🗒 Правила", "👤 Профиль", "📊 Рейтинг")
    keyboard.row("🎮 Новая игра")

    if user_id in get_admins():
        keyboard.row("📄БД","📊Статистика бота","📢 Рассылка")


    return keyboard



@dp.message_handler(text=['игра', '/start','играть','виселица','/game'], state="*")
async def main_start(message: Message, state: FSMContext):
    await state.finish()

    await message.answer("🔸 Бот готов к использованию.\n"
                         "🔸 Если не появились вспомогательные кнопки\n"
                         "▶ Введите /start",
                         reply_markup=menu_frep(message.from_user.id))

async def send_hello(dp):
   await bot.send_message(chat_id=chat_id,text='Арбайтен')


@dp.message_handler(text="🗒 Правила", state="*")
async def new_game (message: Message, state: FSMContext):
    await state.finish()
    await message.answer("Виселица - старая добрая игрушка. Загадывается слово, и Вы буква за буквой пытаетесь его угадать. На это дается 7 попыток.\n"
                         "▶Критерии оценивания:\n"
                         "✅Победа +5 очков\n"
                         "🔥Слово соcтоящие из 10+букв +5 очков\n"
                         "❌Проигрыш -3 очка\n"
                         "⭕Взятие подсказки -2 очка ")

# Получение БД
@dp.message_handler(IsAdmin(), text=['📄БД'], state="*")
async def admin_database(message: Message, state: FSMContext):
    await state.finish()

    with open(PATH_DATABASE, "rb") as document:
        await message.answer_document(document,
                                      caption=f"<b>📦 BACKUP\n"
                                              f"🕰 <code>{get_date()}</code></b>")



@dp.message_handler(text="👤 Профиль", state="*")
async def new_game (message: Message, state: FSMContext):
    await state.finish()
    await message.answer(open_profile_user(message.from_user.id))


@dp.message_handler(text="📊 Рейтинг", state="*")
async def new_game (message: Message, state: FSMContext):
    await state.finish()
    top=[]
    sqlite_connection = sqlite3.connect(PATH_DATABASE)
    cursor = sqlite_connection.cursor()

    sqlite_select_query = """SELECT * from storage_users ORDER BY user_balance DESC"""
    cursor.execute(sqlite_select_query)

    records = cursor.fetchmany(3)
    for row in records:
        top.append(row)

    cursor.close()

    #await message.answer(top[2][2])
    await message.answer(
                         f"🥇Имя: {top[0][2]}          Побед: {top[0][5]}       Очков: {top[0][4]}\n"
                         f"🥈Имя: {top[1][2]}          Побед: {top[1][5]}       Очков: {top[1][4]}\n"
                         f"🥉Имя: {top[2][2]}          Побед: {top[2][5]}       Очков: {top[2][4]}\n")

@dp.message_handler(text="🎮 Новая игра", state="*")
async def cmd_numbers(message: types.Message):
    get_user = get_userx(user_id=message.from_user.id)
    proverka=get_user['user_slovo']
    if proverka == None:

        wrong = 0
        used=[]
        dlina = "➖"
        slov,znach = rand()
        update_slovox(message.from_user.id,
                      user_used="Ты еще не пользовался подсказкой")
        update_slovox(message.from_user.id,
                     user_dlina=len(slov)*dlina)
        update_slovox(message.from_user.id,
                     user_slovo=slov)
        update_slovox(message.from_user.id,
                      user_znach=znach)
        update_slovox(message.from_user.id,
                      user_wrong=wrong)
        #so_far=get_user['user_dlina']
        get_user = get_userx(user_id=message.from_user.id)
        #await update_num_text(message, used, wrong, so_far)

        await message.answer(f"Отгадайте слово: {get_user['user_dlina']}\n Вы использовали следующие буквы: {used}\n {HANGMAN[wrong]}\n 🔸{get_user['user_used']} ", reply_markup=get_keyboard())
    else:
        used=[]
        wrong=get_user['user_wrong']
        await message.answer(f"Отгадайте слово: {get_user['user_dlina']}\n Вы использовали следующие буквы: {used}\n {HANGMAN[wrong]}\n 🔸{get_user['user_used']} ", reply_markup=get_keyboard())




@dp.message_handler(IsAdmin(), text="📊Статистика бота", state="*")
async def admin_statistics(message: Message, state: FSMContext):
    await state.finish()
    top_all=[]
    sqlite_connection = sqlite3.connect(PATH_DATABASE)
    cursor = sqlite_connection.cursor()

    sqlite_select_query = """SELECT * from storage_users ORDER BY user_balance DESC"""
    cursor.execute(sqlite_select_query)

    records = cursor.fetchmany(1000)
    for row in records:
        top_all.append(row[2])
        top_all.append(row[4])

    cursor.close()

    await message.answer(top_all)


"""
###############################################################################ХЕНДЛЕР СНИЗУ НА ЛЮБОЕ СООБЩЕНИЕ КИДАЕТ ВИСЕЛИЦУ
@dp.message_handler()
async def oshibka(message:types.Message):
    get_user = get_userx(user_id=message.from_user.id)
    osh=get_user['user_dlina']


    await message.answer(f"Отгадайте слово: {osh}\n Вы использовали следующие буквы: {used}\n {HANGMAN[wrong]} ", reply_markup=get_keyboard())
"""


def get_keyboard():
    buttons = [
        types.InlineKeyboardButton(text="А", callback_data="num_1"),
        types.InlineKeyboardButton(text="Б", callback_data="num_2"),
        types.InlineKeyboardButton(text="В", callback_data="num_3"),
        types.InlineKeyboardButton(text="Г", callback_data="num_4"),
        types.InlineKeyboardButton(text="Д", callback_data="num_5"),
        types.InlineKeyboardButton(text="Е", callback_data="num_6"),
        types.InlineKeyboardButton(text="Ё", callback_data="num_7"),
        types.InlineKeyboardButton(text="Ж", callback_data="num_8"),
        types.InlineKeyboardButton(text="З", callback_data="num_9"),
        types.InlineKeyboardButton(text="И", callback_data="num_10"),
        types.InlineKeyboardButton(text="Й", callback_data="num_11"),
        types.InlineKeyboardButton(text="К", callback_data="num_12"),
        types.InlineKeyboardButton(text="Л", callback_data="num_13"),
        types.InlineKeyboardButton(text="М", callback_data="num_14"),
        types.InlineKeyboardButton(text="Н", callback_data="num_15"),
        types.InlineKeyboardButton(text="О", callback_data="num_16"),
        types.InlineKeyboardButton(text="П", callback_data="num_17"),
        types.InlineKeyboardButton(text="Р", callback_data="num_18"),
        types.InlineKeyboardButton(text="С", callback_data="num_19"),
        types.InlineKeyboardButton(text="Т", callback_data="num_20"),
        types.InlineKeyboardButton(text="У", callback_data="num_21"),
        types.InlineKeyboardButton(text="Ф", callback_data="num_22"),
        types.InlineKeyboardButton(text="Х", callback_data="num_23"),
        types.InlineKeyboardButton(text="Ц", callback_data="num_24"),
        types.InlineKeyboardButton(text="Ч", callback_data="num_25"),
        types.InlineKeyboardButton(text="Ш", callback_data="num_26"),
        types.InlineKeyboardButton(text="Щ", callback_data="num_27"),
        types.InlineKeyboardButton(text="Ъ", callback_data="num_28"),
        types.InlineKeyboardButton(text="Ы", callback_data="num_29"),
        types.InlineKeyboardButton(text="Ь", callback_data="num_30"),
        types.InlineKeyboardButton(text="Э", callback_data="num_31"),
        types.InlineKeyboardButton(text="Ю", callback_data="num_32"),
        types.InlineKeyboardButton(text="Я", callback_data="num_33"),

        types.InlineKeyboardButton(text="Подсказка", callback_data="podskazka")

       # types.InlineKeyboardButton(text="🎮 Новая игра",callback_data="game")
    ]

    keyboard = types.InlineKeyboardMarkup(row_width=8)
    keyboard.add(*buttons)
    return keyboard

#ОБНОВЛЕНИЕ СООБЩЕНИЯ ВИСЕЛИЦЫ
async def update_num_text(message: types.Message, used: str ,wrong:int,so_far : str ,user_used:str):
    with suppress(MessageNotModified):
        get_user = get_userx(user_id=message.from_user.id)


        await message.answer(f"Отгадайте слово: {so_far}\n Вы использовали следующие буквы: {used}\n {HANGMAN[wrong]}\n {user_used}🔸", reply_markup=get_keyboard())



#обработка кнопки действия
@dp.callback_query_handler(text="num_1")
async def send_bykva_A(callback: types.CallbackQuery):
    get_user = get_userx(user_id=callback.from_user.id)
    slov=get_user['user_slovo']
    bykva_A = "а"
    wrong=get_user['user_wrong']
    used = []
    new = ""
    so_far=get_user['user_dlina']
    user_used=get_user['user_used']
    #so_far=so_far*dlina
    while bykva_A in used:
        pass
    if bykva_A in slov:
        for i in range(len(slov)):  # В цикле добавляем найденную букву в нужное место
            if bykva_A == slov[i]:
                new += bykva_A
            else:
                new += so_far[i]
        so_far = new
        update_slovox(callback.from_user.id,
                      user_dlina=so_far)
        await update_num_text(callback.message, used , wrong , so_far,user_used)
    else:
        used += bykva_A
        wrong = wrong + 1
        update_userx(callback.from_user.id,
                     user_wrong=get_user['user_wrong']+1)
        await update_num_text(callback.message, used , wrong , so_far,user_used)
    if wrong == max_wrong:
        await callback.message.answer(text="🤯 Тебя повесили.\n"
                                                     "🔸 Если не появились вспомогательные кнопки\n"
                                                     "🔸 -3 Очка к твоему Рейтингу\n"
                                                     f"⚡Словом было - {get_user['user_slovo']}\n"
                                                     "♦️ Введите /start")
        update_userx(callback.from_user.id,
                     user_balance=get_user['user_balance']+loose)
        update_userx(callback.from_user.id,
                     user_loose=get_user['user_loose']+1)
        update_userx(callback.from_user.id,
                     user_slovo=None)

    if slov == so_far:
        await callback.message.answer(text="🥳 Ура! Ты смог избежать виселицы.\n"
                                                    "🔸 +5 Очков к твоему Рейтингу\n"
                                                    "▶ Скорей начинай новую игру\n"
                                                    "♦ Введите /start")

        if len(get_user['user_dlina']) >= 10 :
            update_userx(callback.from_user.id,
                         user_balance=get_user['user_balance']+10)

        else:
            update_userx(callback.from_user.id,
                     user_balance=get_user['user_balance']+win)

        update_userx(callback.from_user.id,
                     user_win=get_user['user_win']+1)
        update_userx(callback.from_user.id,
                     user_slovo=None)


@dp.callback_query_handler(text="num_2")
async def send_bykva_A(callback: types.CallbackQuery):
    get_user = get_userx(user_id=callback.from_user.id)
    slov = get_user['user_slovo']
    bykva_A = "б"
    wrong=get_user['user_wrong']
    used = []
    new = ""
    so_far=get_user['user_dlina']
    user_used = get_user['user_used']

    while bykva_A in used:
        pass
    if bykva_A in slov:
        for i in range(len(slov)):  # В цикле добавляем найденную букву в нужное место
            if bykva_A == slov[i]:
                new += bykva_A
            else:
                new += so_far[i]
        so_far = new
        update_slovox(callback.from_user.id,
                      user_dlina=so_far)
        await update_num_text(callback.message, used , wrong , so_far,user_used)
    else:
        used += bykva_A
        wrong = wrong + 1
        update_userx(callback.from_user.id,
                     user_wrong=get_user['user_wrong']+1)
        await update_num_text(callback.message, used , wrong , so_far,user_used)
    if wrong == max_wrong:
        await callback.message.answer(text="🤯 Тебя повесили.\n"
                                                     "🔸 Если не появились вспомогательные кнопки\n"
                                                     "🔸 -3 Очка к твоему Рейтингу\n"
                                                     f"⚡Словом было - {get_user['user_slovo']}\n"
                                                     "♦ Введите /start")
        update_userx(callback.from_user.id,
                     user_balance=get_user['user_balance']+loose)
        update_userx(callback.from_user.id,
                     userloose=get_user['user_loose']+1)
        update_userx(callback.from_user.id,
                     user_slovo=None)


    if slov == so_far:
        await callback.message.answer(text="🥳 Ура! Ты смог избежать виселицы.\n"
                                                    "🔸 +5 Очков к твоему Рейтингу\n"
                                                    "▶ Скорей начинай новую игру\n"
                                           " ♦ Введите /start   ")

        if len(get_user['user_dlina']) >= 10 :
            update_userx(callback.from_user.id,
                         user_balance=get_user['user_balance']+10)

        else:
            update_userx(callback.from_user.id,
                     user_balance=get_user['user_balance']+win)

        update_userx(callback.from_user.id,
                     user_win=get_user['user_win']+1)
        update_userx(callback.from_user.id,
                     user_slovo=None)


@dp.callback_query_handler(text="num_3")
async def send_bykva_A(callback: types.CallbackQuery):
    get_user = get_userx(user_id=callback.from_user.id)
    slov = get_user['user_slovo']
    bykva_A = "в"
    wrong=get_user['user_wrong']
    used = []
    new = ""
    so_far=get_user['user_dlina']
    user_used = get_user['user_used']

    while bykva_A in used:
        pass
    if bykva_A in slov:
        for i in range(len(slov)):  # В цикле добавляем найденную букву в нужное место
            if bykva_A == slov[i]:
                new += bykva_A
            else:
                new += so_far[i]
        so_far = new
        update_slovox(callback.from_user.id,
                      user_dlina=so_far)
        await update_num_text(callback.message, used , wrong , so_far,user_used)
    else:
        used += bykva_A
        wrong = wrong + 1
        update_userx(callback.from_user.id,
                     user_wrong=get_user['user_wrong']+1)
        await update_num_text(callback.message, used , wrong , so_far,user_used)
    if wrong == max_wrong:
        await callback.message.answer(text="🤯 Тебя повесили.\n"
                                                     "🔸 Если не появились вспомогательные кнопки\n"
                                                     "🔸 -3 Очка к твоему Рейтингу\n"
                                                     f"⚡Словом было - {get_user['user_slovo']}\n"
                                                     "♦ Введите /start")
        update_userx(callback.from_user.id,
                     user_balance=get_user['user_balance']+loose)
        update_userx(callback.from_user.id,
                     user_loose=get_user['user_loose']+1)
        update_userx(callback.from_user.id,
                     user_slovo=None)

    if slov == so_far:
        await callback.message.answer(text="🥳 Ура! Ты смог избежать виселицы.\n"
                                                    "🔸 +5 Очков к твоему Рейтингу\n"
                                                    "▶ Скорей начинай новую игру\n"
                                           "♦ Введите /start")

        if len(get_user['user_dlina']) >= 10 :
            update_userx(callback.from_user.id,
                         user_balance=get_user['user_balance']+10)

        else:
            update_userx(callback.from_user.id,
                     user_balance=get_user['user_balance']+win)

        update_userx(callback.from_user.id,
                     user_win=get_user['user_win']+1)
        update_userx(callback.from_user.id,
                     user_slovo=None)


@dp.callback_query_handler(text="num_4")
async def send_bykva_A(callback: types.CallbackQuery):
    get_user = get_userx(user_id=callback.from_user.id)
    slov = get_user['user_slovo']
    bykva_A = "г"
    wrong=get_user['user_wrong']
    used = []
    new = ""
    so_far=get_user['user_dlina']
    user_used = get_user['user_used']

    while bykva_A in used:
        pass
    if bykva_A in slov:
        for i in range(len(slov)):  # В цикле добавляем найденную букву в нужное место
            if bykva_A == slov[i]:
                new += bykva_A
            else:
                new += so_far[i]
        so_far = new
        update_slovox(callback.from_user.id,
                      user_dlina=so_far)
        await update_num_text(callback.message, used , wrong , so_far,user_used)
    else:
        used += bykva_A
        wrong = wrong + 1
        update_userx(callback.from_user.id,
                     user_wrong=get_user['user_wrong']+1)
        await update_num_text(callback.message, used , wrong , so_far,user_used)
    if wrong == max_wrong:
        await callback.message.answer(text="🤯 Тебя повесили.\n"
                                                     "🔸 Если не появились вспомогательные кнопки\n"
                                                     "🔸 -3 Очка к твоему Рейтингу\n"
                                                     f"⚡Словом было - {get_user['user_slovo']}\n"
                                                     "♦ Введите /start")

        update_userx(callback.from_user.id,
                     user_balance=get_user['user_balance']+loose)
        update_userx(callback.from_user.id,
                     user_loose=get_user['user_loose']+1)
        update_userx(callback.from_user.id,
                     user_slovo=None)

    if slov == so_far:
        await callback.message.answer(text="🥳 Ура! Ты смог избежать виселицы.\n"
                                                    "🔸 +5 Очков к твоему Рейтингу\n"
                                                    "▶ Скорей начинай новую игру\n"
                                           "♦ Введите /start")

        if len(get_user['user_dlina']) >= 10 :
            update_userx(callback.from_user.id,
                         user_balance=get_user['user_balance']+10)

        else:
            update_userx(callback.from_user.id,
                     user_balance=get_user['user_balance']+win)

        update_userx(callback.from_user.id,
                     user_win=get_user['user_win']+1)
        update_userx(callback.from_user.id,
                     user_slovo=None)


@dp.callback_query_handler(text="num_5")
async def send_bykva_A(callback: types.CallbackQuery):
    get_user = get_userx(user_id=callback.from_user.id)
    slov = get_user['user_slovo']
    bykva_A = "д"
    wrong=get_user['user_wrong']
    used = []
    new = ""
    so_far=get_user['user_dlina']
    user_used = get_user['user_used']

    while bykva_A in used:
        pass
    if bykva_A in slov:
        for i in range(len(slov)):  # В цикле добавляем найденную букву в нужное место
            if bykva_A == slov[i]:
                new += bykva_A
            else:
                new += so_far[i]
        so_far = new
        update_slovox(callback.from_user.id,
                      user_dlina=so_far)
        await update_num_text(callback.message, used , wrong , so_far,user_used)
    else:
        used += bykva_A
        wrong = wrong + 1
        update_userx(callback.from_user.id,
                     user_wrong=get_user['user_wrong']+1)
        await update_num_text(callback.message, used , wrong , so_far,user_used)
    if wrong == max_wrong:
        await callback.message.answer(text="🤯 Тебя повесили.\n"
                                                     "🔸 Если не появились вспомогательные кнопки\n"
                                                     "🔸 -3 Очка к твоему Рейтингу\n"
                                                     f"⚡Словом было - {get_user['user_slovo']}\n"
                                                     "♦ Введите /start")
        update_userx(callback.from_user.id,
                     user_balance=get_user['user_balance']+loose)
        update_userx(callback.from_user.id,
                     user_loose=get_user['user_loose']+1)
        update_userx(callback.from_user.id,
                     user_slovo=None)

    if slov == so_far:
        await callback.message.answer(text="🥳 Ура! Ты смог избежать виселицы.\n"
                                                    "🔸 +5 Очков к твоему Рейтингу\n"
                                                    "▶ Скорей начинай новую игру\n"
                                           "♦ Введите /start")

        if len(get_user['user_dlina']) >= 10 :
            update_userx(callback.from_user.id,
                         user_balance=get_user['user_balance']+10)

        else:
            update_userx(callback.from_user.id,
                     user_balance=get_user['user_balance']+win)

        update_userx(callback.from_user.id,
                     user_win=get_user['user_win']+1)
        update_userx(callback.from_user.id,
                     user_slovo=None)


@dp.callback_query_handler(text="num_6")
async def send_bykva_A(callback: types.CallbackQuery):
    get_user = get_userx(user_id=callback.from_user.id)
    slov = get_user['user_slovo']
    bykva_A = "е"
    wrong=get_user['user_wrong']
    used = []
    new = ""
    so_far=get_user['user_dlina']
    user_used = get_user['user_used']

    while bykva_A in used:
        pass
    if bykva_A in slov:
        for i in range(len(slov)):  # В цикле добавляем найденную букву в нужное место
            if bykva_A == slov[i]:
                new += bykva_A
            else:
                new += so_far[i]
        so_far = new
        update_slovox(callback.from_user.id,
                      user_dlina=so_far)
        await update_num_text(callback.message, used , wrong , so_far,user_used)
    else:
        used += bykva_A
        wrong = wrong + 1
        update_userx(callback.from_user.id,
                     user_wrong=get_user['user_wrong']+1)
        await update_num_text(callback.message, used , wrong , so_far,user_used)
    if wrong == max_wrong:
        await callback.message.answer(text="🤯 Тебя повесили.\n"
                                                     "🔸 Если не появились вспомогательные кнопки\n"
                                                     "🔸 -3 Очка к твоему Рейтингу\n"
                                                     f"⚡Словом было - {get_user['user_slovo']}\n"
                                                     "♦ Введите /start")
        update_userx(callback.from_user.id,
                     user_balance=get_user['user_balance']+loose)
        update_userx(callback.from_user.id,
                     user_loose=get_user['user_loose']+1)
        update_userx(callback.from_user.id,
                     user_slovo=None)

    if slov == so_far:
        await callback.message.answer(text="🥳 Ура! Ты смог избежать виселицы.\n"
                                                    "🔸 +5 Очков к твоему Рейтингу\n"
                                                    "▶ Скорей начинай новую игру\n"
                                           "♦ Введите /start")


        if len(get_user['user_dlina']) >= 10 :
            update_userx(callback.from_user.id,
                         user_balance=get_user['user_balance']+10)

        else:
            update_userx(callback.from_user.id,
                     user_balance=get_user['user_balance']+win)

        update_userx(callback.from_user.id,
                     user_win=get_user['user_win']+1)
        update_userx(callback.from_user.id,
                     user_slovo=None)



@dp.callback_query_handler(text="num_7")
async def send_bykva_A(callback: types.CallbackQuery):
    get_user = get_userx(user_id=callback.from_user.id)
    slov = get_user['user_slovo']
    bykva_A = "ё"
    wrong=get_user['user_wrong']
    used = []
    new = ""
    so_far=get_user['user_dlina']
    user_used = get_user['user_used']

    while bykva_A in used:
        pass
    if bykva_A in slov:
        for i in range(len(slov)):  # В цикле добавляем найденную букву в нужное место
            if bykva_A == slov[i]:
                new += bykva_A
            else:
                new += so_far[i]
        so_far = new
        update_slovox(callback.from_user.id,
                      user_dlina=so_far)
        await update_num_text(callback.message, used , wrong , so_far,user_used)
    else:
        used += bykva_A
        wrong = wrong + 1
        update_userx(callback.from_user.id,
                     user_wrong=get_user['user_wrong']+1)
        await update_num_text(callback.message, used , wrong , so_far,user_used)
    if wrong == max_wrong:
        await callback.message.answer(text="🤯 Тебя повесили.\n"
                                                     "🔸 Если не появились вспомогательные кнопки\n"
                                                     "🔸 -3 Очка к твоему Рейтингу\n"
                                                     f"⚡Словом было - {get_user['user_slovo']}\n"
                                                     "♦ Введите /start")
        update_userx(callback.from_user.id,
                     user_balance=get_user['user_balance']+loose)
        update_userx(callback.from_user.id,
                     user_loose=get_user['user_loose']+1)
        update_userx(callback.from_user.id,
                     user_slovo=None)


    if slov == so_far:
        await callback.message.answer(text="🥳 Ура! Ты смог избежать виселицы.\n"
                                                    "🔸 +5 Очков к твоему Рейтингу\n"
                                                    "▶ Скорей начинай новую игру\n"
                                           "♦ Введите /start")

        if len(get_user['user_dlina']) >= 10 :
            update_userx(callback.from_user.id,
                         user_balance=get_user['user_balance']+10)

        else:
            update_userx(callback.from_user.id,
                     user_balance=get_user['user_balance']+win)

        update_userx(callback.from_user.id,
                     user_win=get_user['user_win']+1)
        update_userx(callback.from_user.id,
                     user_slovo=None)


@dp.callback_query_handler(text="num_8")
async def send_bykva_A(callback: types.CallbackQuery):
    get_user = get_userx(user_id=callback.from_user.id)
    slov = get_user['user_slovo']
    bykva_A = "ж"
    wrong=get_user['user_wrong']
    used = []
    new = ""
    so_far=get_user['user_dlina']
    user_used = get_user['user_used']

    while bykva_A in used:
        pass
    if bykva_A in slov:
        for i in range(len(slov)):  # В цикле добавляем найденную букву в нужное место
            if bykva_A == slov[i]:
                new += bykva_A
            else:
                new += so_far[i]
        so_far = new
        update_slovox(callback.from_user.id,
                      user_dlina=so_far)
        await update_num_text(callback.message, used , wrong , so_far,user_used)
    else:
        used += bykva_A
        wrong = wrong + 1
        update_userx(callback.from_user.id,
                     user_wrong=get_user['user_wrong']+1)
        await update_num_text(callback.message, used , wrong , so_far,user_used)
    if wrong == max_wrong:
        await callback.message.answer(text="🤯 Тебя повесили.\n"
                                                     "🔸 Если не появились вспомогательные кнопки\n"
                                                     "🔸 -3 Очка к твоему Рейтингу\n"
                                                     f"⚡Словом было - {get_user['user_slovo']}\n"
                                                     "♦ Введите /start")
        update_userx(callback.from_user.id,
                     user_balance=get_user['user_balance']+loose)
        update_userx(callback.from_user.id,
                     user_loose=get_user['user_loose']+1)
        update_userx(callback.from_user.id,
                     user_slovo=None)

    if slov == so_far:
        await callback.message.answer(text="🥳 Ура! Ты смог избежать виселицы.\n"
                                                    "🔸 +5 Очков к твоему Рейтингу\n"
                                                    "▶ Скорей начинай новую игру\n"
                                           "♦ Введите /start")

        if len(get_user['user_dlina']) >= 10 :
            update_userx(callback.from_user.id,
                         user_balance=get_user['user_balance']+10)

        else:
            update_userx(callback.from_user.id,
                     user_balance=get_user['user_balance']+win)

        update_userx(callback.from_user.id,
                     user_win=get_user['user_win']+1)
        update_userx(callback.from_user.id,
                     user_slovo=None)


@dp.callback_query_handler(text="num_9")
async def send_bykva_A(callback: types.CallbackQuery):
    get_user = get_userx(user_id=callback.from_user.id)
    slov = get_user['user_slovo']
    bykva_A = "з"
    wrong=get_user['user_wrong']
    used = []
    new = ""
    so_far=get_user['user_dlina']
    user_used = get_user['user_used']

    while bykva_A in used:
        pass
    if bykva_A in slov:
        for i in range(len(slov)):  # В цикле добавляем найденную букву в нужное место
            if bykva_A == slov[i]:
                new += bykva_A
            else:
                new += so_far[i]
        so_far = new
        update_slovox(callback.from_user.id,
                      user_dlina=so_far)
        await update_num_text(callback.message, used , wrong , so_far,user_used)
    else:
        used += bykva_A
        wrong = wrong + 1
        update_userx(callback.from_user.id,
                     user_wrong=get_user['user_wrong']+1)
        await update_num_text(callback.message, used , wrong ,  so_far,user_used)
    if wrong == max_wrong:
        await callback.message.answer(text="🤯 Тебя повесили.\n"
                                                     "🔸 Если не появились вспомогательные кнопки\n"
                                                     "🔸 -3 Очка к твоему Рейтингу\n"
                                                     f"⚡Словом было - {get_user['user_slovo']}\n"
                                                     "♦ Введите /start")
        update_userx(callback.from_user.id,
                     user_balance=get_user['user_balance']+loose)
        update_userx(callback.from_user.id,
                     user_loose=get_user['user_loose']+1)
        update_userx(callback.from_user.id,
                     user_slovo=None)

    if slov == so_far:
        await callback.message.answer(text="🥳 Ура! Ты смог избежать виселицы.\n"
                                                    "🔸 +5 Очков к твоему Рейтингу\n"
                                                    "▶ Скорей начинай новую игру\n"
                                           "♦ Введите /start")

        if len(get_user['user_dlina']) >= 10 :
            update_userx(callback.from_user.id,
                         user_balance=get_user['user_balance']+10)

        else:
            update_userx(callback.from_user.id,
                     user_balance=get_user['user_balance']+win)

        update_userx(callback.from_user.id,
                     user_win=get_user['user_win']+1)
        update_userx(callback.from_user.id,
                     user_slovo=None)



@dp.callback_query_handler(text="num_10")
async def send_bykva_A(callback: types.CallbackQuery):
    get_user = get_userx(user_id=callback.from_user.id)
    slov = get_user['user_slovo']
    bykva_A = "и"
    wrong=get_user['user_wrong']
    used = []
    new = ""
    so_far=get_user['user_dlina']
    user_used = get_user['user_used']

    while bykva_A in used:
        pass
    if bykva_A in slov:
        for i in range(len(slov)):  # В цикле добавляем найденную букву в нужное место
            if bykva_A == slov[i]:
                new += bykva_A
            else:
                new += so_far[i]
        so_far = new
        update_slovox(callback.from_user.id,
                      user_dlina=so_far)
        await update_num_text(callback.message, used , wrong , so_far,user_used)
    else:
        used += bykva_A
        wrong = wrong + 1
        update_userx(callback.from_user.id,
                     user_wrong=get_user['user_wrong']+1)
        await update_num_text(callback.message, used , wrong , so_far,user_used)
    if wrong == max_wrong:
        await callback.message.answer(text="🤯 Тебя повесили.\n"
                                                     "🔸 Если не появились вспомогательные кнопки\n"
                                                     "🔸 -3 Очка к твоему Рейтингу\n"
                                                     f"⚡Словом было - {get_user['user_slovo']}\n"
                                                     "♦ Введите /start")
        update_userx(callback.from_user.id,
                     user_balance=get_user['user_balance']+loose)
        update_userx(callback.from_user.id,
                     user_loose=get_user['user_loose']+1)
        update_userx(callback.from_user.id,
                     user_slovo=None)

    if slov == so_far:
        await callback.message.answer(text="🥳 Ура! Ты смог избежать виселицы.\n"
                                                    "🔸 +5 Очков к твоему Рейтингу\n"
                                                    "▶ Скорей начинай новую игру\n"
                                    "♦ Введите /start")


        if len(get_user['user_dlina']) >= 10 :
            update_userx(callback.from_user.id,
                         user_balance=get_user['user_balance']+10)

        else:
            update_userx(callback.from_user.id,
                     user_balance=get_user['user_balance']+win)

        update_userx(callback.from_user.id,
                     user_win=get_user['user_win']+1)
        update_userx(callback.from_user.id,
                     user_slovo=None)



@dp.callback_query_handler(text="num_11")
async def send_bykva_A(callback: types.CallbackQuery):
    get_user = get_userx(user_id=callback.from_user.id)
    slov = get_user['user_slovo']
    bykva_A = "й"
    wrong=get_user['user_wrong']
    used = []
    new = ""
    so_far=get_user['user_dlina']
    user_used = get_user['user_used']

    while bykva_A in used:
        pass
    if bykva_A in slov:
        for i in range(len(slov)):  # В цикле добавляем найденную букву в нужное место
            if bykva_A == slov[i]:
                new += bykva_A
            else:
                new += so_far[i]
        so_far = new
        update_slovox(callback.from_user.id,
                      user_dlina=so_far)
        await update_num_text(callback.message, used , wrong , so_far,user_used)
    else:
        used += bykva_A
        wrong = wrong + 1
        update_userx(callback.from_user.id,
                     user_wrong=get_user['user_wrong']+1)
        await update_num_text(callback.message, used , wrong , so_far,user_used)
    if wrong == max_wrong:
        await callback.message.answer(text="🤯 Тебя повесили.\n"
                                                     "🔸 Если не появились вспомогательные кнопки\n"
                                                     "🔸 -3 Очка к твоему Рейтингу\n"
                                                     f"⚡Словом было - {get_user['user_slovo']}\n"
                                                     "♦ Введите /start")
        update_userx(callback.from_user.id,
                     user_balance=get_user['user_balance']+loose)
        update_userx(callback.from_user.id,
                     user_loose=get_user['user_loose']+1)
        update_userx(callback.from_user.id,
                     user_slovo=None)

    if slov == so_far:
        await callback.message.answer(text="🥳 Ура! Ты смог избежать виселицы.\n"
                                                    "🔸 +5 Очков к твоему Рейтингу\n"
                                                    "▶ Скорей начинай новую игру\n"
                                           "♦ Введите /start")

        if len(get_user['user_dlina']) >= 10 :
            update_userx(callback.from_user.id,
                         user_balance=get_user['user_balance']+10)

        else:
            update_userx(callback.from_user.id,
                     user_balance=get_user['user_balance']+win)

        update_userx(callback.from_user.id,
                     user_win=get_user['user_win']+1)
        update_userx(callback.from_user.id,
                     user_slovo=None)


@dp.callback_query_handler(text="num_12")
async def send_bykva_A(callback: types.CallbackQuery):
    get_user = get_userx(user_id=callback.from_user.id)
    slov = get_user['user_slovo']
    bykva_A = "к"
    wrong=get_user['user_wrong']
    used = []
    new = ""
    so_far=get_user['user_dlina']
    user_used = get_user['user_used']

    while bykva_A in used:
        pass
    if bykva_A in slov:
        for i in range(len(slov)):  # В цикле добавляем найденную букву в нужное место
            if bykva_A == slov[i]:
                new += bykva_A
            else:
                new += so_far[i]
        so_far = new
        update_slovox(callback.from_user.id,
                      user_dlina=so_far)
        await update_num_text(callback.message, used , wrong , so_far,user_used)
    else:
        used += bykva_A
        wrong = wrong + 1
        update_userx(callback.from_user.id,
                     user_wrong=get_user['user_wrong']+1)
        await update_num_text(callback.message, used , wrong , so_far,user_used)
    if wrong == max_wrong:
        await callback.message.answer(text="🤯 Тебя повесили.\n"
                                                     "🔸 Если не появились вспомогательные кнопки\n"
                                                     "🔸 -3 Очка к твоему Рейтингу\n"
                                                     f"⚡Словом было - {get_user['user_slovo']}\n"
                                                     "♦ Введите /start")
        update_userx(callback.from_user.id,
                     user_balance=get_user['user_balance']+loose)
        update_userx(callback.from_user.id,
                     user_loose=get_user['user_loose']+1)
        update_userx(callback.from_user.id,
                     user_slovo=None)

    if slov == so_far:
        await callback.message.answer(text="🥳 Ура! Ты смог избежать виселицы.\n"
                                                    "🔸 +5 Очков к твоему Рейтингу\n"
                                                    "▶ Скорей начинай новую игру\n"
                                           "♦ Введите /start")

        if len(get_user['user_dlina']) >= 10 :
            update_userx(callback.from_user.id,
                         user_balance=get_user['user_balance']+10)

        else:
            update_userx(callback.from_user.id,
                     user_balance=get_user['user_balance']+win)

        update_userx(callback.from_user.id,
                     user_win=get_user['user_win']+1)
        update_userx(callback.from_user.id,
                     user_slovo=None)



@dp.callback_query_handler(text="num_13")
async def send_bykva_A(callback: types.CallbackQuery):
    get_user = get_userx(user_id=callback.from_user.id)
    slov = get_user['user_slovo']
    bykva_A = "л"
    wrong=get_user['user_wrong']
    used = []
    new = ""
    so_far=get_user['user_dlina']
    update_slovox(callback.from_user.id,
                  user_dlina=so_far)
    user_used = get_user['user_used']
    while bykva_A in used:
        pass
    if bykva_A in slov:
        for i in range(len(slov)):  # В цикле добавляем найденную букву в нужное место
            if bykva_A == slov[i]:
                new += bykva_A
            else:
                new += so_far[i]
        so_far = new
        update_slovox(callback.from_user.id,
                      user_dlina=so_far)
        await update_num_text(callback.message, used , wrong , so_far,user_used)
    else:
        used += bykva_A
        wrong = wrong + 1
        update_userx(callback.from_user.id,
                     user_wrong=get_user['user_wrong']+1)
        await update_num_text(callback.message, used , wrong , so_far,user_used)
    if wrong == max_wrong:
        await callback.message.answer(text="🤯 Тебя повесили.\n"
                                                     "🔸 Если не появились вспомогательные кнопки\n"
                                                     "🔸 -3 Очка к твоему Рейтингу\n"
                                                     f"⚡Словом было - {get_user['user_slovo']}\n"
                                                     "♦ Введите /start")
        update_userx(callback.from_user.id,
                     user_balance=get_user['user_balance']+loose)
        update_userx(callback.from_user.id,
                     user_loose=get_user['user_loose']+1)
        update_userx(callback.from_user.id,
                     user_slovo=None)

    if slov == so_far:
        await callback.message.answer(text="🥳 Ура! Ты смог избежать виселицы.\n"
                                                    "🔸 +5 Очков к твоему Рейтингу\n"
                                                    "▶ Скорей начинай новую игру\n"
                                           "♦ Введите /start")


        if len(get_user['user_dlina']) >= 10 :
            update_userx(callback.from_user.id,
                         user_balance=get_user['user_balance']+10)

        else:
            update_userx(callback.from_user.id,
                     user_balance=get_user['user_balance']+win)

        update_userx(callback.from_user.id,
                     user_win=get_user['user_win']+1)
        update_userx(callback.from_user.id,
                     user_slovo=None)



@dp.callback_query_handler(text="num_14")
async def send_bykva_A(callback: types.CallbackQuery):
    get_user = get_userx(user_id=callback.from_user.id)
    slov = get_user['user_slovo']
    bykva_A = "м"
    wrong=get_user['user_wrong']
    used = []
    new = ""
    so_far=get_user['user_dlina']
    user_used = get_user['user_used']
    while bykva_A in used:
        pass
    if bykva_A in slov:
        for i in range(len(slov)):  # В цикле добавляем найденную букву в нужное место
            if bykva_A == slov[i]:
                new += bykva_A
            else:
                new += so_far[i]
        so_far = new
        update_slovox(callback.from_user.id,
                      user_dlina=so_far)
        await update_num_text(callback.message, used , wrong , so_far,user_used)
    else:
        used += bykva_A
        wrong = wrong + 1
        update_userx(callback.from_user.id,
                     user_wrong=get_user['user_wrong']+1)
        await update_num_text(callback.message, used , wrong , so_far,user_used)
    if wrong == max_wrong:
        await callback.message.answer(text="🤯 Тебя повесили.\n"
                                                     "🔸 Если не появились вспомогательные кнопки\n"
                                                     "🔸 -3 Очка к твоему Рейтингу\n"
                                                     f"⚡Словом было - {get_user['user_slovo']}\n"
                                                     "♦ Введите /start")
        update_userx(callback.from_user.id,
                     user_balance=get_user['user_balance']+loose)
        update_userx(callback.from_user.id,
                     user_loose=get_user['user_loose']+1)
        update_userx(callback.from_user.id,
                     user_slovo=None)

    if slov == so_far:
        await callback.message.answer(text="🥳 Ура! Ты смог избежать виселицы.\n"
                                                    "🔸 +5 Очков к твоему Рейтингу\n"
                                                    "▶ Скорей начинай новую игру\n"
                                           "♦ Введите /start")

        if len(get_user['user_dlina']) >= 10 :
            update_userx(callback.from_user.id,
                         user_balance=get_user['user_balance']+10)

        else:
            update_userx(callback.from_user.id,
                     user_balance=get_user['user_balance']+win)

        update_userx(callback.from_user.id,
                     user_win=get_user['user_win']+1)
        update_userx(callback.from_user.id,
                     user_slovo=None)


@dp.callback_query_handler(text="num_15")
async def send_bykva_A(callback: types.CallbackQuery):
    get_user = get_userx(user_id=callback.from_user.id)
    slov = get_user['user_slovo']
    bykva_A = "н"
    wrong=get_user['user_wrong']
    used = []
    new = ""
    so_far=get_user['user_dlina']
    user_used = get_user['user_used']
    while bykva_A in used:
        pass
    if bykva_A in slov:
        for i in range(len(slov)):  # В цикле добавляем найденную букву в нужное место
            if bykva_A == slov[i]:
                new += bykva_A
            else:
                new += so_far[i]
        so_far = new
        update_slovox(callback.from_user.id,
                      user_dlina=so_far)
        await update_num_text(callback.message, used , wrong , so_far,user_used)
    else:
        used += bykva_A
        wrong = wrong + 1
        update_userx(callback.from_user.id,
                     user_wrong=get_user['user_wrong']+1)
        await update_num_text(callback.message, used , wrong , so_far,user_used)
    if wrong == max_wrong:
        await callback.message.answer(text="🤯 Тебя повесили.\n"
                                                     "🔸 Если не появились вспомогательные кнопки\n"
                                                     "🔸 -3 Очка к твоему Рейтингу\n"
                                                     f"⚡Словом было - {get_user['user_slovo']}\n"
                                                     "♦ Введите /start")
        update_userx(callback.from_user.id,
                     user_balance=get_user['user_balance']+loose)
        update_userx(callback.from_user.id,
                     user_loose=get_user['user_loose']+1)
        update_userx(callback.from_user.id,
                     user_slovo=None)

    if slov == so_far:
        await callback.message.answer(text="🥳 Ура! Ты смог избежать виселицы.\n"
                                                    "🔸 +5 Очков к твоему Рейтингу\n"
                                                    "▶ Скорей начинай новую игру\n"
                                           "♦ Введите /start")

        if len(get_user['user_dlina']) >= 10 :
            update_userx(callback.from_user.id,
                         user_balance=get_user['user_balance']+10)

        else:
            update_userx(callback.from_user.id,
                     user_balance=get_user['user_balance']+win)

        update_userx(callback.from_user.id,
                     user_win=get_user['user_win']+1)
        update_userx(callback.from_user.id,
                     user_slovo=None)


@dp.callback_query_handler(text="num_16")
async def send_bykva_A(callback: types.CallbackQuery):
    get_user = get_userx(user_id=callback.from_user.id)
    slov = get_user['user_slovo']
    bykva_A = "о"
    wrong=get_user['user_wrong']
    used = []
    new = ""
    so_far=get_user['user_dlina']
    user_used = get_user['user_used']
    while bykva_A in used:
        pass
    if bykva_A in slov:
        for i in range(len(slov)):  # В цикле добавляем найденную букву в нужное место
            if bykva_A == slov[i]:
                new += bykva_A
            else:
                new += so_far[i]
        so_far = new
        update_slovox(callback.from_user.id,
                      user_dlina=so_far)
        await update_num_text(callback.message, used , wrong , so_far,user_used)
    else:
        used += bykva_A
        wrong = wrong + 1
        update_userx(callback.from_user.id,
                     user_wrong=get_user['user_wrong']+1)
        await update_num_text(callback.message, used , wrong , so_far,user_used)
    if wrong == max_wrong:
        await callback.message.answer(text="🤯 Тебя повесили.\n"
                                                     "🔸 Если не появились вспомогательные кнопки\n"
                                                     "🔸 -3 Очка к твоему Рейтингу\n"
                                                     f"⚡Словом было - {get_user['user_slovo']}\n"
                                                     "♦ Введите /start")
        update_userx(callback.from_user.id,
                     user_balance=get_user['user_balance']+loose)
        update_userx(callback.from_user.id,
                     user_loose=get_user['user_loose']+1)
        update_userx(callback.from_user.id,
                     user_slovo=None)

    if slov == so_far:
        await callback.message.answer(text="🥳 Ура! Ты смог избежать виселицы.\n"
                                                    "🔸 +5 Очков к твоему Рейтингу\n"
                                                    "▶ Скорей начинай новую игру\n"
                                           "♦ Введите /start")

        if len(get_user['user_dlina']) >= 10 :
            update_userx(callback.from_user.id,
                         user_balance=get_user['user_balance']+10)

        else:
            update_userx(callback.from_user.id,
                     user_balance=get_user['user_balance']+win)

        update_userx(callback.from_user.id,
                     user_win=get_user['user_win']+1)
        update_userx(callback.from_user.id,
                     user_slovo=None)



@dp.callback_query_handler(text="num_17")
async def send_bykva_A(callback: types.CallbackQuery):
    get_user = get_userx(user_id=callback.from_user.id)
    slov = get_user['user_slovo']
    bykva_A = "п"
    wrong=get_user['user_wrong']
    used = []
    new = ""
    so_far=get_user['user_dlina']
    user_used = get_user['user_used']
    while bykva_A in used:
        pass
    if bykva_A in slov:
        for i in range(len(slov)):  # В цикле добавляем найденную букву в нужное место
            if bykva_A == slov[i]:
                new += bykva_A
            else:
                new += so_far[i]
        so_far = new
        update_slovox(callback.from_user.id,
                      user_dlina=so_far)
        await update_num_text(callback.message, used , wrong , so_far,user_used)
    else:
        used += bykva_A
        wrong = wrong + 1
        update_userx(callback.from_user.id,
                     user_wrong=get_user['user_wrong']+1)
        await update_num_text(callback.message, used , wrong , so_far,user_used)
    if wrong == max_wrong:
        await callback.message.answer(text="🤯 Тебя повесили.\n"
                                                     "🔸 Если не появились вспомогательные кнопки\n"
                                                     "🔸 -3 Очка к твоему Рейтингу\n"
                                                     f"⚡Словом было - {get_user['user_slovo']}\n"
                                                     "♦ Введите /start")
        update_userx(callback.from_user.id,
                     user_balance=get_user['user_balance']+loose)
        update_userx(callback.from_user.id,
                     user_loose=get_user['user_loose']+1)
        update_userx(callback.from_user.id,
                     user_slovo=None)

    if slov == so_far:
        await callback.message.answer(text="🥳 Ура! Ты смог избежать виселицы.\n"
                                                    "🔸 +5 Очков к твоему Рейтингу\n"
                                                    "▶ Скорей начинай новую игру\n"
                                           "♦ Введите /start")

        if len(get_user['user_dlina']) >= 10 :
            update_userx(callback.from_user.id,
                         user_balance=get_user['user_balance']+10)

        else:
            update_userx(callback.from_user.id,
                     user_balance=get_user['user_balance']+win)

        update_userx(callback.from_user.id,
                     user_win=get_user['user_win']+1)
        update_userx(callback.from_user.id,
                     user_slovo=None)



@dp.callback_query_handler(text="num_18")
async def send_bykva_A(callback: types.CallbackQuery):
    get_user = get_userx(user_id=callback.from_user.id)
    slov = get_user['user_slovo']
    bykva_A = "р"
    wrong=get_user['user_wrong']
    used = []
    new = ""
    so_far=get_user['user_dlina']
    user_used = get_user['user_used']
    while bykva_A in used:
        pass
    if bykva_A in slov:
        for i in range(len(slov)):  # В цикле добавляем найденную букву в нужное место
            if bykva_A == slov[i]:
                new += bykva_A
            else:
                new += so_far[i]
        so_far = new
        update_slovox(callback.from_user.id,
                      user_dlina=so_far)
        await update_num_text(callback.message, used , wrong , so_far,user_used)
    else:
        used += bykva_A
        wrong = wrong + 1
        update_userx(callback.from_user.id,
                     user_wrong=get_user['user_wrong']+1)
        await update_num_text(callback.message, used , wrong , so_far,user_used)
    if wrong == max_wrong:
        await callback.message.answer(text="🤯 Тебя повесили.\n"
                                                     "🔸 Если не появились вспомогательные кнопки\n"
                                                     "🔸 -3 Очка к твоему Рейтингу\n"
                                                     f"⚡Словом было - {get_user['user_slovo']}\n"
                                                     "♦ Введите /start")
        update_userx(callback.from_user.id,
                     user_balance=get_user['user_balance']+loose)
        update_userx(callback.from_user.id,
                     user_loose=get_user['user_loose']+1)
        update_userx(callback.from_user.id,
                     user_slovo=None)

    if slov == so_far:
        await callback.message.answer(text="🥳 Ура! Ты смог избежать виселицы.\n"
                                                    "🔸 +5 Очков к твоему Рейтингу\n"
                                                    "▶ Скорей начинай новую игру\n"
                                           "♦ Введите /start")


        if len(get_user['user_dlina']) >= 10 :
            update_userx(callback.from_user.id,
                         user_balance=get_user['user_balance']+10)

        else:
            update_userx(callback.from_user.id,
                     user_balance=get_user['user_balance']+win)

        update_userx(callback.from_user.id,
                     user_win=get_user['user_win']+1)
        update_userx(callback.from_user.id,
                     user_slovo=None)


@dp.callback_query_handler(text="num_19")
async def send_bykva_A(callback: types.CallbackQuery):
    get_user = get_userx(user_id=callback.from_user.id)
    slov = get_user['user_slovo']
    bykva_A = "с"
    wrong=get_user['user_wrong']
    used = []
    new = ""
    so_far=get_user['user_dlina']
    user_used = get_user['user_used']
    while bykva_A in used:
        pass
    if bykva_A in slov:
        for i in range(len(slov)):  # В цикле добавляем найденную букву в нужное место
            if bykva_A == slov[i]:
                new += bykva_A
            else:
                new += so_far[i]
        so_far = new
        update_slovox(callback.from_user.id,
                      user_dlina=so_far)
        await update_num_text(callback.message, used , wrong , so_far,user_used)
    else:
        used += bykva_A
        wrong = wrong + 1
        update_userx(callback.from_user.id,
                     user_wrong=get_user['user_wrong']+1)
        await update_num_text(callback.message, used , wrong , so_far,user_used)
    if wrong == max_wrong:
        await callback.message.answer(text="🤯 Тебя повесили.\n"
                                                     "🔸 Если не появились вспомогательные кнопки\n"
                                                     "🔸 -3 Очка к твоему Рейтингу\n"
                                                     f"⚡Словом было - {get_user['user_slovo']}\n"
                                                     "♦ Введите /start")
        update_userx(callback.from_user.id,
                     user_balance=get_user['user_balance']+loose)
        update_userx(callback.from_user.id,
                     user_loose=get_user['user_loose']+1)
        update_userx(callback.from_user.id,
                     user_slovo=None)

    if slov == so_far:
        await callback.message.answer(text="🥳 Ура! Ты смог избежать виселицы.\n"
                                                    "🔸 +5 Очков к твоему Рейтингу\n"
                                                    "▶ Скорей начинай новую игру\n"
                                           "♦ Введите /start")

        if len(get_user['user_dlina']) >= 10 :
            update_userx(callback.from_user.id,
                         user_balance=get_user['user_balance']+10)

        else:
            update_userx(callback.from_user.id,
                     user_balance=get_user['user_balance']+win)

        update_userx(callback.from_user.id,
                     user_win=get_user['user_win']+1)
        update_userx(callback.from_user.id,
                     user_slovo=None)


@dp.callback_query_handler(text="num_20")
async def send_bykva_A(callback: types.CallbackQuery):
    get_user = get_userx(user_id=callback.from_user.id)
    slov = get_user['user_slovo']
    bykva_A = "т"
    wrong=get_user['user_wrong']
    used = []
    new = ""
    so_far=get_user['user_dlina']
    user_used = get_user['user_used']
    while bykva_A in used:
        pass
    if bykva_A in slov:
        for i in range(len(slov)):  # В цикле добавляем найденную букву в нужное место
            if bykva_A == slov[i]:
                new += bykva_A
            else:
                new += so_far[i]
        so_far = new
        update_slovox(callback.from_user.id,
                      user_dlina=so_far)
        await update_num_text(callback.message, used , wrong , so_far,user_used)
    else:
        used += bykva_A
        wrong = wrong + 1
        update_userx(callback.from_user.id,
                     user_wrong=get_user['user_wrong']+1)
        await update_num_text(callback.message, used , wrong , so_far,user_used)
    if wrong == max_wrong:
        await callback.message.answer(text="🤯 Тебя повесили.\n"
                                                     "🔸 Если не появились вспомогательные кнопки\n"
                                                     "🔸 -3 Очка к твоему Рейтингу\n"
                                                     f"⚡Словом было - {get_user['user_slovo']}\n"
                                                     "♦ Введите /start")
        update_userx(callback.from_user.id,
                     user_balance=get_user['user_balance']+loose)
        update_userx(callback.from_user.id,
                     user_loose=get_user['user_loose']+1)
        update_userx(callback.from_user.id,
                     user_slovo=None)

    if slov == so_far:
        await callback.message.answer(text="🥳 Ура! Ты смог избежать виселицы.\n"
                                                    "🔸 +5 Очков к твоему Рейтингу\n"
                                                    "▶ Скорей начинай новую игру\n"
                                           "♦ Введите /start")


        if len(get_user['user_dlina']) >= 10 :
            update_userx(callback.from_user.id,
                         user_balance=get_user['user_balance']+10)

        else:
            update_userx(callback.from_user.id,
                     user_balance=get_user['user_balance']+win)

        update_userx(callback.from_user.id,
                     user_win=get_user['user_win']+1)
        update_userx(callback.from_user.id,
                     user_slovo=None)


@dp.callback_query_handler(text="num_21")
async def send_bykva_A(callback: types.CallbackQuery):
    get_user = get_userx(user_id=callback.from_user.id)
    slov = get_user['user_slovo']
    bykva_A = "у"
    wrong=get_user['user_wrong']
    used = []
    new = ""
    so_far=get_user['user_dlina']
    user_used = get_user['user_used']
    while bykva_A in used:
        pass
    if bykva_A in slov:
        for i in range(len(slov)):  # В цикле добавляем найденную букву в нужное место
            if bykva_A == slov[i]:
                new += bykva_A
            else:
                new += so_far[i]
        so_far = new
        update_slovox(callback.from_user.id,
                      user_dlina=so_far)
        await update_num_text(callback.message, used , wrong , so_far,user_used)
    else:
        used += bykva_A
        wrong = wrong + 1
        update_userx(callback.from_user.id,
                     user_wrong=get_user['user_wrong']+1)
        await update_num_text(callback.message, used , wrong , so_far,user_used)
    if wrong == max_wrong:
        await callback.message.answer(text="🤯 Тебя повесили.\n"
                                                     "🔸 Если не появились вспомогательные кнопки\n"
                                                     "🔸 -3 Очка к твоему Рейтингу\n"
                                                     f"⚡Словом было - {get_user['user_slovo']}\n"
                                                     "♦ Введите /start")
        update_userx(callback.from_user.id,
                     user_balance=get_user['user_balance']+loose)
        update_userx(callback.from_user.id,
                     user_loose=get_user['user_loose']+1)
        update_userx(callback.from_user.id,
                     user_slovo=None)

    if slov == so_far:
        await callback.message.answer(text="🥳 Ура! Ты смог избежать виселицы.\n"
                                                    "🔸 +5 Очков к твоему Рейтингу\n"
                                                    "▶ Скорей начинай новую игру\n"
                                           "♦ Введите /start")

        if len(get_user['user_dlina']) >= 10 :
            update_userx(callback.from_user.id,
                         user_balance=get_user['user_balance']+10)

        else:
            update_userx(callback.from_user.id,
                     user_balance=get_user['user_balance']+win)

        update_userx(callback.from_user.id,
                     user_win=get_user['user_win']+1)
        update_userx(callback.from_user.id,
                     user_slovo=None)



@dp.callback_query_handler(text="num_22")
async def send_bykva_A(callback: types.CallbackQuery):
    get_user = get_userx(user_id=callback.from_user.id)
    slov = get_user['user_slovo']
    bykva_A = "ф"
    wrong=get_user['user_wrong']
    used = []
    new = ""
    so_far=get_user['user_dlina']
    user_used = get_user['user_used']
    while bykva_A in used:
        pass
    if bykva_A in slov:
        for i in range(len(slov)):  # В цикле добавляем найденную букву в нужное место
            if bykva_A == slov[i]:
                new += bykva_A
            else:
                new += so_far[i]
        so_far = new
        update_slovox(callback.from_user.id,
                      user_dlina=so_far)
        await update_num_text(callback.message, used , wrong , so_far,user_used)
    else:
        used += bykva_A
        wrong = wrong + 1
        update_userx(callback.from_user.id,
                     user_wrong=get_user['user_wrong']+1)
        await update_num_text(callback.message, used , wrong , so_far,user_used)
    if wrong == max_wrong:
        await callback.message.answer(text="🤯 Тебя повесили.\n"
                                                     "🔸 Если не появились вспомогательные кнопки\n"
                                                     "🔸 -3 Очка к твоему Рейтингу\n"
                                                     f"⚡Словом было - {get_user['user_slovo']}\n"
                                                     "♦ Введите /start")
        update_userx(callback.from_user.id,
                     user_balance=get_user['user_balance']+loose)
        update_userx(callback.from_user.id,
                     user_loose=get_user['user_loose']+1)
        update_userx(callback.from_user.id,
                     user_slovo=None)

    if slov == so_far:
        await callback.message.answer(text="🥳 Ура! Ты смог избежать виселицы.\n"
                                                    "🔸 +5 Очков к твоему Рейтингу\n"
                                                    "▶ Скорей начинай новую игру\n"
                                           "♦ Введите /start")


        if len(get_user['user_dlina']) >= 10 :
            update_userx(callback.from_user.id,
                         user_balance=get_user['user_balance']+10)

        else:
            update_userx(callback.from_user.id,
                     user_balance=get_user['user_balance']+win)

        update_userx(callback.from_user.id,
                     user_win=get_user['user_win']+1)
        update_userx(callback.from_user.id,
                     user_slovo=None)


@dp.callback_query_handler(text="num_23")
async def send_bykva_A(callback: types.CallbackQuery):
    get_user = get_userx(user_id=callback.from_user.id)
    slov = get_user['user_slovo']
    bykva_A = "х"
    wrong=get_user['user_wrong']
    used = []
    new = ""
    so_far=get_user['user_dlina']
    user_used = get_user['user_used']
    while bykva_A in used:
        pass
    if bykva_A in slov:
        for i in range(len(slov)):  # В цикле добавляем найденную букву в нужное место
            if bykva_A == slov[i]:
                new += bykva_A
            else:
                new += so_far[i]
        so_far = new
        update_slovox(callback.from_user.id,
                      user_dlina=so_far)
        await update_num_text(callback.message, used , wrong , so_far,user_used)
    else:
        used += bykva_A
        wrong = wrong + 1
        update_userx(callback.from_user.id,
                     user_wrong=get_user['user_wrong']+1)
        await update_num_text(callback.message, used , wrong , so_far,user_used)
    if wrong == max_wrong:
        await callback.message.answer(text="🤯 Тебя повесили.\n"
                                                     "🔸 Если не появились вспомогательные кнопки\n"
                                                     "🔸 -3 Очка к твоему Рейтингу\n"
                                                     f"⚡Словом было - {get_user['user_slovo']}\n"
                                                     "♦ Введите /start")
        update_userx(callback.from_user.id,
                     user_balance=get_user['user_balance']+loose)
        update_userx(callback.from_user.id,
                     user_loose=get_user['user_loose']+1)
        update_userx(callback.from_user.id,
                     user_slovo=None)

    if slov == so_far:
        await callback.message.answer(text="🥳 Ура! Ты смог избежать виселицы.\n"
                                                    "🔸 +5 Очков к твоему Рейтингу\n"
                                                    "▶ Скорей начинай новую игру\n"
                                           "♦ Введите /start")

        if len(get_user['user_dlina']) >= 10 :
            update_userx(callback.from_user.id,
                         user_balance=get_user['user_balance']+10)

        else:
            update_userx(callback.from_user.id,
                     user_balance=get_user['user_balance']+win)

        update_userx(callback.from_user.id,
                     user_win=get_user['user_win']+1)
        update_userx(callback.from_user.id,
                     user_slovo=None)



@dp.callback_query_handler(text="num_24")
async def send_bykva_A(callback: types.CallbackQuery):
    get_user = get_userx(user_id=callback.from_user.id)
    slov = get_user['user_slovo']
    bykva_A = "ц"
    wrong=get_user['user_wrong']
    used = []
    new = ""
    so_far=get_user['user_dlina']
    user_used = get_user['user_used']
    while bykva_A in used:
        pass
    if bykva_A in slov:
        for i in range(len(slov)):  # В цикле добавляем найденную букву в нужное место
            if bykva_A == slov[i]:
                new += bykva_A
            else:
                new += so_far[i]
        so_far = new
        update_slovox(callback.from_user.id,
                      user_dlina=so_far)
        await update_num_text(callback.message, used , wrong , so_far,user_used)
    else:
        used += bykva_A
        wrong = wrong + 1
        update_userx(callback.from_user.id,
                     user_wrong=get_user['user_wrong']+1)
        await update_num_text(callback.message, used , wrong , so_far,user_used)
    if wrong == max_wrong:
        await callback.message.answer(text="🤯 Тебя повесили.\n"
                                                     "🔸 Если не появились вспомогательные кнопки\n"
                                                     "🔸 -3 Очка к твоему Рейтингу\n"
                                                     f"⚡Словом было - {get_user['user_slovo']}\n"
                                                     "♦ Введите /start")
        update_userx(callback.from_user.id,
                     user_balance=get_user['user_balance']+loose)
        update_userx(callback.from_user.id,
                     user_loose=get_user['user_loose']+1)
        update_userx(callback.from_user.id,
                     user_slovo=None)

    if slov == so_far:
        await callback.message.answer(text="🥳 Ура! Ты смог избежать виселицы.\n"
                                                    "🔸 +5 Очков к твоему Рейтингу\n"
                                                    "▶ Скорей начинай новую игру\n"
                                           "♦ Введите /start")


        if len(get_user['user_dlina']) >= 10 :
            update_userx(callback.from_user.id,
                         user_balance=get_user['user_balance']+10)

        else:
            update_userx(callback.from_user.id,
                     user_balance=get_user['user_balance']+win)

        update_userx(callback.from_user.id,
                     user_win=get_user['user_win']+1)
        update_userx(callback.from_user.id,
                     user_slovo=None)


@dp.callback_query_handler(text="num_25")
async def send_bykva_A(callback: types.CallbackQuery):
    get_user = get_userx(user_id=callback.from_user.id)
    slov = get_user['user_slovo']
    bykva_A = "ч"
    wrong=get_user['user_wrong']
    used = []
    new = ""
    so_far=get_user['user_dlina']
    user_used = get_user['user_used']
    while bykva_A in used:
        pass
    if bykva_A in slov:
        for i in range(len(slov)):  # В цикле добавляем найденную букву в нужное место
            if bykva_A == slov[i]:
                new += bykva_A
            else:
                new += so_far[i]
        so_far = new
        update_slovox(callback.from_user.id,
                      user_dlina=so_far)
        await update_num_text(callback.message, used , wrong , so_far,user_used)
    else:
        used += bykva_A
        wrong = wrong + 1
        update_userx(callback.from_user.id,
                     user_wrong=get_user['user_wrong']+1)
        await update_num_text(callback.message, used , wrong , so_far,user_used)
    if wrong == max_wrong:
        await callback.message.answer(text="🤯 Тебя повесили.\n"
                                                     "🔸 Если не появились вспомогательные кнопки\n"
                                                     "🔸 -3 Очка к твоему Рейтингу\n"
                                                     f"⚡Словом было - {get_user['user_slovo']}\n"
                                                     "♦ Введите /start")
        update_userx(callback.from_user.id,
                     user_balance=get_user['user_balance']+loose)
        update_userx(callback.from_user.id,
                     user_loose=get_user['user_loose']+1)
        update_userx(callback.from_user.id,
                     user_slovo=None)


    if slov == so_far:
        await callback.message.answer(text="🥳 Ура! Ты смог избежать виселицы.\n"
                                                    "🔸 +5 Очков к твоему Рейтингу\n"
                                                    "▶ Скорей начинай новую игру\n"
                                           "♦ Введите /start")

        if len(get_user['user_dlina']) >= 10 :
            update_userx(callback.from_user.id,
                         user_balance=get_user['user_balance']+10)

        else:
            update_userx(callback.from_user.id,
                     user_balance=get_user['user_balance']+win)

        update_userx(callback.from_user.id,
                     user_win=get_user['user_win']+1)
        update_userx(callback.from_user.id,
                     user_slovo=None)


@dp.callback_query_handler(text="num_26")
async def send_bykva_A(callback: types.CallbackQuery):
    get_user = get_userx(user_id=callback.from_user.id)
    slov = get_user['user_slovo']
    bykva_A = "ш"
    wrong=get_user['user_wrong']
    used = []
    new = ""
    so_far=get_user['user_dlina']
    user_used = get_user['user_used']
    while bykva_A in used:
        pass
    if bykva_A in slov:
        for i in range(len(slov)):  # В цикле добавляем найденную букву в нужное место
            if bykva_A == slov[i]:
                new += bykva_A
            else:
                new += so_far[i]
        so_far = new
        update_slovox(callback.from_user.id,
                      user_dlina=so_far)
        await update_num_text(callback.message, used , wrong , so_far,user_used)
    else:
        used += bykva_A
        wrong = wrong + 1
        update_userx(callback.from_user.id,
                     user_wrong=get_user['user_wrong']+1)
        await update_num_text(callback.message, used , wrong , so_far,user_used)
    if wrong == max_wrong:
        await callback.message.answer(text="🤯 Тебя повесили.\n"
                                                     "🔸 Если не появились вспомогательные кнопки\n"
                                                     "🔸 -3 Очка к твоему Рейтингу\n"
                                                     f"⚡Словом было - {get_user['user_slovo']}\n"
                                                     "♦ Введите /start")
        update_userx(callback.from_user.id,
                     user_balance=get_user['user_balance']+loose)
        update_userx(callback.from_user.id,
                     user_loose=get_user['user_loose']+1)
        update_userx(callback.from_user.id,
                     user_slovo=None)

    if slov == so_far:
        await callback.message.answer(text="🥳 Ура! Ты смог избежать виселицы.\n"
                                                    "🔸 +5 Очков к твоему Рейтингу\n"
                                                    "▶ Скорей начинай новую игру\n"
                                           "♦ Введите /start")

        if len(get_user['user_dlina']) >= 10 :
            update_userx(callback.from_user.id,
                         user_balance=get_user['user_balance']+10)

        else:
            update_userx(callback.from_user.id,
                     user_balance=get_user['user_balance']+win)

        update_userx(callback.from_user.id,
                     user_win=get_user['user_win']+1)
        update_userx(callback.from_user.id,
                     user_slovo=None)




@dp.callback_query_handler(text="num_27")
async def send_bykva_A(callback: types.CallbackQuery):
    get_user = get_userx(user_id=callback.from_user.id)
    slov = get_user['user_slovo']
    bykva_A = "щ"
    wrong=get_user['user_wrong']
    used = []
    new = ""
    so_far=get_user['user_dlina']
    user_used = get_user['user_used']
    while bykva_A in used:
        pass
    if bykva_A in slov:
        for i in range(len(slov)):  # В цикле добавляем найденную букву в нужное место
            if bykva_A == slov[i]:
                new += bykva_A
            else:
                new += so_far[i]
        so_far = new
        update_slovox(callback.from_user.id,
                      user_dlina=so_far)
        await update_num_text(callback.message, used , wrong , so_far,user_used)
    else:
        used += bykva_A
        wrong = wrong + 1
        update_userx(callback.from_user.id,
                     user_wrong=get_user['user_wrong']+1)
        await update_num_text(callback.message, used , wrong , so_far,user_used)
    if wrong == max_wrong:
        await callback.message.answer(text="🤯 Тебя повесили.\n"
                                                     "🔸 Если не появились вспомогательные кнопки\n"
                                                     "🔸 -3 Очка к твоему Рейтингу\n"
                                                     f"⚡Словом было - {get_user['user_slovo']}\n"
                                                     "♦ Введите /start")
        update_userx(callback.from_user.id,
                     user_balance=get_user['user_balance']+loose)
        update_userx(callback.from_user.id,
                     user_loose=get_user['user_loose']+1)
        update_userx(callback.from_user.id,
                     user_slovo=None)

    if slov == so_far:
        await callback.message.answer(text="🥳 Ура! Ты смог избежать виселицы.\n"
                                                    "🔸 +5 Очков к твоему Рейтингу\n"
                                                    "▶ Скорей начинай новую игру\n"
                                           "♦ Введите /start")

        if len(get_user['user_dlina']) >= 10 :
            update_userx(callback.from_user.id,
                         user_balance=get_user['user_balance']+10)

        else:
            update_userx(callback.from_user.id,
                     user_balance=get_user['user_balance']+win)

        update_userx(callback.from_user.id,
                     user_win=get_user['user_win']+1)
        update_userx(callback.from_user.id,
                     user_slovo=None)




@dp.callback_query_handler(text="num_28")
async def send_bykva_A(callback: types.CallbackQuery):
    get_user = get_userx(user_id=callback.from_user.id)
    slov = get_user['user_slovo']
    bykva_A = "ъ"
    wrong=get_user['user_wrong']
    used = []
    new = ""
    so_far=get_user['user_dlina']
    user_used = get_user['user_used']
    while bykva_A in used:
        pass
    if bykva_A in slov:
        for i in range(len(slov)):  # В цикле добавляем найденную букву в нужное место
            if bykva_A == slov[i]:
                new += bykva_A
            else:
                new += so_far[i]
        so_far = new
        update_slovox(callback.from_user.id,
                      user_dlina=so_far)
        await update_num_text(callback.message, used , wrong ,  so_far,user_used)
    else:
        used += bykva_A
        wrong = wrong + 1
        update_userx(callback.from_user.id,
                     user_wrong=get_user['user_wrong']+1)
        await update_num_text(callback.message, used , wrong , so_far,user_used)
    if wrong == max_wrong:
        await callback.message.answer(text="🤯 Тебя повесили.\n"
                                                     "🔸 Если не появились вспомогательные кнопки\n"
                                                     "🔸 -3 Очка к твоему Рейтингу\n"
                                                     f"⚡Словом было - {get_user['user_slovo']}\n"
                                                     "♦ Введите /start")
        update_userx(callback.from_user.id,
                     user_balance=get_user['user_balance']+loose)
        update_userx(callback.from_user.id,
                     user_loose=get_user['user_loose']+1)
        update_userx(callback.from_user.id,
                     user_slovo=None)

    if slov == so_far:
        await callback.message.answer(text="🥳 Ура! Ты смог избежать виселицы.\n"
                                                    "🔸 +5 Очков к твоему Рейтингу\n"
                                                    "▶ Скорей начинай новую игру\n"
                                           "♦ Введите /start")

        if len(get_user['user_dlina']) >= 10 :
            update_userx(callback.from_user.id,
                         user_balance=get_user['user_balance']+10)

        else:
            update_userx(callback.from_user.id,
                     user_balance=get_user['user_balance']+win)

        update_userx(callback.from_user.id,
                     user_win=get_user['user_win']+1)
        update_userx(callback.from_user.id,
                     user_slovo=None)


@dp.callback_query_handler(text="num_29")
async def send_bykva_A(callback: types.CallbackQuery):
    get_user = get_userx(user_id=callback.from_user.id)
    slov = get_user['user_slovo']
    bykva_A = "ы"
    wrong=get_user['user_wrong']
    used = []
    new = ""
    so_far=get_user['user_dlina']
    user_used = get_user['user_used']
    while bykva_A in used:
        pass
    if bykva_A in slov:
        for i in range(len(slov)):  # В цикле добавляем найденную букву в нужное место
            if bykva_A == slov[i]:
                new += bykva_A
            else:
                new += so_far[i]
        so_far = new
        update_slovox(callback.from_user.id,
                      user_dlina=so_far)
        await update_num_text(callback.message, used , wrong , so_far,user_used)
    else:
        used += bykva_A
        wrong = wrong + 1
        update_userx(callback.from_user.id,
                     user_wrong=get_user['user_wrong']+1)
        await update_num_text(callback.message, used , wrong , so_far,user_used)
    if wrong == max_wrong:
        await callback.message.answer(text="🤯 Тебя повесили.\n"
                                                     "🔸 Если не появились вспомогательные кнопки\n"
                                                     "🔸 -3 Очка к твоему Рейтингу\n"
                                                     f"⚡Словом было - {get_user['user_slovo']}\n"
                                                     "♦ Введите /start")
        update_userx(callback.from_user.id,
                     user_balance=get_user['user_balance']+loose)
        update_userx(callback.from_user.id,
                     user_loose=get_user['user_loose']+1)
        update_userx(callback.from_user.id,
                     user_slovo=None)

    if slov == so_far:
        await callback.message.answer(text="🥳 Ура! Ты смог избежать виселицы.\n"
                                                    "🔸 +5 Очков к твоему Рейтингу\n"
                                                    "▶ Скорей начинай новую игру\n"
                                           "♦ Введите /start")

        if len(get_user['user_dlina']) >= 10 :
            update_userx(callback.from_user.id,
                         user_balance=get_user['user_balance']+10)

        else:
            update_userx(callback.from_user.id,
                     user_balance=get_user['user_balance']+win)

        update_userx(callback.from_user.id,
                     user_win=get_user['user_win']+1)
        update_userx(callback.from_user.id,
                     user_slovo=None)




@dp.callback_query_handler(text="num_30")
async def send_bykva_A(callback: types.CallbackQuery):
    get_user = get_userx(user_id=callback.from_user.id)
    slov = get_user['user_slovo']
    bykva_A = "ь"
    wrong=get_user['user_wrong']
    used = []
    new = ""
    so_far=get_user['user_dlina']
    user_used = get_user['user_used']
    while bykva_A in used:
        pass
    if bykva_A in slov:
        for i in range(len(slov)):  # В цикле добавляем найденную букву в нужное место
            if bykva_A == slov[i]:
                new += bykva_A
            else:
                new += so_far[i]
        so_far = new
        update_slovox(callback.from_user.id,
                      user_dlina=so_far)
        await update_num_text(callback.message, used , wrong , so_far,user_used)
    else:
        used += bykva_A
        wrong = wrong + 1
        update_userx(callback.from_user.id,
                     user_wrong=get_user['user_wrong']+1)
        await update_num_text(callback.message, used , wrong , so_far,user_used)
    if wrong == max_wrong:
        await callback.message.answer(text="🤯 Тебя повесили.\n"
                                                     "🔸 Если не появились вспомогательные кнопки\n"
                                                     "🔸 -3 Очка к твоему Рейтингу\n"
                                                     f"⚡Словом было - {get_user['user_slovo']}\n"
                                                     "♦ Введите /start")
        update_userx(callback.from_user.id,
                     user_balance=get_user['user_balance']+loose)
        update_userx(callback.from_user.id,
                     user_loose=get_user['user_loose']+1)
        update_userx(callback.from_user.id,
                     user_slovo=None)

    if slov == so_far:
        await callback.message.answer(text="🥳 Ура! Ты смог избежать виселицы.\n"
                                                    "🔸 +5 Очков к твоему Рейтингу\n"
                                                    "▶ Скорей начинай новую игру\n"
                                           "♦ Введите /start")


        if len(get_user['user_dlina']) >= 10 :
            update_userx(callback.from_user.id,
                         user_balance=get_user['user_balance']+10)

        else:
            update_userx(callback.from_user.id,
                     user_balance=get_user['user_balance']+win)

        update_userx(callback.from_user.id,
                     user_win=get_user['user_win']+1)
        update_userx(callback.from_user.id,
                     user_slovo=None)



@dp.callback_query_handler(text="num_31")
async def send_bykva_A(callback: types.CallbackQuery):
    get_user = get_userx(user_id=callback.from_user.id)
    slov = get_user['user_slovo']
    bykva_A = "э"
    wrong=get_user['user_wrong']
    used = []
    new = ""
    so_far=get_user['user_dlina']
    user_used = get_user['user_used']
    while bykva_A in used:
        pass
    if bykva_A in slov:
        for i in range(len(slov)):  # В цикле добавляем найденную букву в нужное место
            if bykva_A == slov[i]:
                new += bykva_A
            else:
                new += so_far[i]
        so_far = new
        update_slovox(callback.from_user.id,
                      user_dlina=so_far)
        await update_num_text(callback.message, used , wrong , so_far,user_used)
    else:
        used += bykva_A
        wrong = wrong + 1
        update_userx(callback.from_user.id,
                     user_wrong=get_user['user_wrong']+1)
        await update_num_text(callback.message, used , wrong , so_far,user_used)
    if wrong == max_wrong:
        await callback.message.answer(text="🤯 Тебя повесили.\n"
                                                     "🔸 Если не появились вспомогательные кнопки\n"
                                                     "🔸 -3 Очка к твоему Рейтингу\n"
                                                     f"⚡Словом было - {get_user['user_slovo']}\n"
                                                     "♦ Введите /start")
        update_userx(callback.from_user.id,
                     user_balance=get_user['user_balance']+loose)
        update_userx(callback.from_user.id,
                     user_loose=get_user['user_loose']+1)
        update_userx(callback.from_user.id,
                     user_slovo=None)



    if slov == so_far:
        await callback.message.answer(text="🥳 Ура! Ты смог избежать виселицы.\n"
                                                    "🔸 +5 Очков к твоему Рейтингу\n"
                                                    "▶ Скорей начинай новую игру\n"
                                           "♦ Введите /start")

        if len(get_user['user_dlina']) >= 10 :
            update_userx(callback.from_user.id,
                         user_balance=get_user['user_balance']+10)

        else:
            update_userx(callback.from_user.id,
                     user_balance=get_user['user_balance']+win)

        update_userx(callback.from_user.id,
                     user_win=get_user['user_win']+1)
        update_userx(callback.from_user.id,
                     user_slovo=None)



@dp.callback_query_handler(text="num_32")
async def send_bykva_A(callback: types.CallbackQuery):
    get_user = get_userx(user_id=callback.from_user.id)
    slov = get_user['user_slovo']
    bykva_A = "ю"
    wrong=get_user['user_wrong']
    used = []
    new = ""
    so_far=get_user['user_dlina']
    user_used = get_user['user_used']
    while bykva_A in used:
        pass
    if bykva_A in slov:
        for i in range(len(slov)):  # В цикле добавляем найденную букву в нужное место
            if bykva_A == slov[i]:
                new += bykva_A
            else:
                new += so_far[i]
        so_far = new
        update_slovox(callback.from_user.id,
                      user_dlina=so_far)
        await update_num_text(callback.message, used , wrong ,so_far,user_used)
    else:
        used += bykva_A
        wrong = wrong + 1
        update_userx(callback.from_user.id,
                     user_wrong=get_user['user_wrong']+1)
        await update_num_text(callback.message, used , wrong , so_far,user_used)
    if wrong == max_wrong:
        await callback.message.answer(text="🤯 Тебя повесили.\n"
                                                     "🔸 Если не появились вспомогательные кнопки\n"
                                                     "🔸 -3 Очка к твоему Рейтингу\n"
                                                     f"⚡Словом было - {get_user['user_slovo']}\n"
                                                     "♦ Введите /start")
        update_userx(callback.from_user.id,
                     user_balance=get_user['user_balance']+loose)
        update_userx(callback.from_user.id,
                     user_loose=get_user['user_loose']+1)
        update_userx(callback.from_user.id,
                     user_slovo=None)
    if slov == so_far:
        await callback.message.answer(text="🥳 Ура! Ты смог избежать виселицы.\n"
                                                    "🔸 +5 Очков к твоему Рейтингу\n"
                                                    "▶ Скорей начинай новую игру\n"
                                           "♦ Введите /start")

        if len(get_user['user_dlina']) >= 10 :
            update_userx(callback.from_user.id,
                         user_balance=get_user['user_balance']+10)

        else:
            update_userx(callback.from_user.id,
                     user_balance=get_user['user_balance']+win)

        update_userx(callback.from_user.id,
                     user_win=get_user['user_win']+1)
        update_userx(callback.from_user.id,
                     user_slovo=None)




@dp.callback_query_handler(text="num_33")
async def send_bykva_A(callback: types.CallbackQuery):
    get_user = get_userx(user_id=callback.from_user.id)
    slov = get_user['user_slovo']
    bykva_A = "я"
    wrong=get_user['user_wrong']
    used = []
    new = ""
    so_far=get_user['user_dlina']
    update_slovox(callback.from_user.id,
                  user_dlina=so_far)
    user_used = get_user['user_used']
    while bykva_A in used:
        pass
    if bykva_A in slov:
        for i in range(len(slov)):  # В цикле добавляем найденную букву в нужное место
            if bykva_A == slov[i]:
                new += bykva_A
            else:
                new += so_far[i]
        so_far = new
        update_slovox(callback.from_user.id,
                      user_dlina=so_far)
        await update_num_text(callback.message, used , wrong , so_far,user_used)
    else:
        used += bykva_A
        wrong = wrong + 1
        update_userx(callback.from_user.id,
                     user_wrong=get_user['user_wrong']+1)
        await update_num_text(callback.message, used , wrong , so_far,user_used)
    if wrong == max_wrong:
        await callback.message.answer(text="🤯 Тебя повесили.\n"
                                                     "🔸 Если не появились вспомогательные кнопки\n"
                                                     "🔸 -3 Очка к твоему Рейтингу\n"
                                                     f"⚡Словом было - {get_user['user_slovo']}\n"
                                                     "▶ Введите /start")
        update_userx(callback.from_user.id,
                     user_balance=get_user['user_balance']+loose)
        update_userx(callback.from_user.id,
                     user_loose=get_user['user_loose']+1)
        update_userx(callback.from_user.id,
                     user_slovo=None)

    if slov == so_far:
        await callback.message.answer(text="🥳 Ура! Ты смог избежать виселицы.\n"
                                                    "🔸 +5 Очков к твоему Рейтингу\n"
                                                    "▶ Скорей начинай новую игру\n"
                                           "♦ Введите /start")

        if len(get_user['user_dlina']) >= 10 :
            update_userx(callback.from_user.id,
                         user_balance=get_user['user_balance']+10)

        else:
            update_userx(callback.from_user.id,
                     user_balance=get_user['user_balance']+win)

        update_userx(callback.from_user.id,
                     user_win=get_user['user_win']+1)
        update_userx(callback.from_user.id,
                     user_slovo=None)



@dp.callback_query_handler(text="podskazka")
async def send_podskazka(callback: types.CallbackQuery):
    get_user = get_userx(user_id=callback.from_user.id)
    await callback.message.answer(text=f"{get_user['user_znach']}\n"
                                               f"🔸 -2 Очка твоего Рейтинга")
    slov=get_user['user_znach']
    update_userx(callback.from_user.id,
                 user_balance=get_user['user_balance']+podz)
    update_slovox(callback.from_user.id,
                 user_used=slov)

########################################################РАССЫЛКА
@dp.message_handler(IsAdmin(), text="📢 Рассылка", state="*")
async def functions_mail(message: Message, state: FSMContext):
    await state.finish()

    await state.set_state("here_mail_text")
    await message.answer("<b>📢 Введите текст для рассылки пользователям</b>\n"
                         "❕ Вы можете использовать HTML разметку")

@dp.message_handler(IsAdmin(), state="here_mail_text")
async def functions_mail_get(message: Message, state: FSMContext):
    await state.update_data(here_mail_text="📢 Рассылка.\n" + str(message.text))
    get_users = get_all_usersx()

    try:
        cache_msg = await message.answer(message.text)
        await cache_msg.delete()

        await state.set_state("here_mail_confirm")
        await message.answer(
            f"<b>📢 Отправить <code>{len(get_users)}</code> юзерам сообщение?</b>\n"
            f"{message.text}",
            reply_markup=mail_confirm_inl,
            disable_web_page_preview=True
        )
    except CantParseEntities:
        await message.answer("<b>❌ Ошибка синтаксиса HTML.</b>\n"
                             "📢 Введите текст для рассылки пользователям.\n"
                             "❕ Вы можете использовать HTML разметку.")


# Подтверждение отправки рассылки
@dp.callback_query_handler(IsAdmin(), text_startswith="confirm_mail", state="here_mail_confirm")
async def functions_mail_confirm(call: CallbackQuery, state: FSMContext):
    get_action = call.data.split(":")[1]

    send_message = (await state.get_data())['here_mail_text']
    get_users = get_all_usersx()
    await state.finish()

    if get_action == "yes":
        await call.message.edit_text(f"<b>📢 Рассылка началась... (0/{len(get_users)})</b>")
        asyncio.create_task(functions_mail_make(send_message, call))
    else:
        await call.message.edit_text("<b>📢 Вы отменили отправку рассылки ✅</b>")


# Сама отправка рассылки
async def functions_mail_make(message, call: CallbackQuery):
    receive_users, block_users, how_users = 0, 0, 0
    get_users = get_all_usersx()
    get_time = get_unix()

    for user in get_users:
        try:
            await bot.send_message(user['user_id'], message, disable_web_page_preview=True)
            receive_users += 1
        except:
            block_users += 1

        how_users += 1

        if how_users % 10 == 0:
            await call.message.edit_text(f"<b>📢 Рассылка началась... ({how_users}/{len(get_users)})</b>")

        await asyncio.sleep(0.08)

    await call.message.edit_text(
        f"<b>📢 Рассылка была завершена за <code>{get_unix() - get_time}сек</code></b>\n"
        f"👤 Всего пользователей: <code>{len(get_users)}</code>\n"
        f"✅ Пользователей получило сообщение: <code>{receive_users}</code>\n"
        f"❌ Пользователей не получило сообщение: <code>{block_users}</code>"
    )

