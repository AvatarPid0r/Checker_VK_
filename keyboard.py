import sqlite3
from config import admin
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup


async def cmd_starting_(user_id) -> ReplyKeyboardMarkup:
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    m1 = KeyboardButton('👀Просмотр пользователей')
    m2 = KeyboardButton('🗑Удалить все ID')
    m3 = KeyboardButton('✏Добавить по штучно')
    m4 = KeyboardButton('✏Добавить списком')
    markup.row(m1).add(m3, m4).add(m2)
    if user_id in admin:
        m5 = KeyboardButton('💠Добавить пользователя')
        m6 = KeyboardButton('👻Удалить пользователя')
        markup.add(m5, m6)
    return markup

async def delet() -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    m2 = InlineKeyboardButton('Да', callback_data='delete_all')
    markup.add(m2)
    return markup


async def send_opovos(user_id) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    with sqlite3.connect('database.db') as con:
        cur = con.cursor()
        cur.execute('SELECT status FROM user_id WHERE user_id = ?', (user_id,))
        row = cur.fetchone()
        if row[0] == 1:
            m1 = InlineKeyboardButton('Оповещение ✅', callback_data='yes')
        else:
            m1 = InlineKeyboardButton('Оповещение ❌', callback_data='no')
        markup.add(m1)
    return markup
