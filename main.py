import re
import sqlite3
import time

import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import asyncio
import logging
from aiogram import executor
from aiogram.dispatcher import FSMContext
from aiogram.types import BotCommand
from config import BotFather, vk_api
from keyboard import *
from base import *
from vk_checker import check_user
from state import Users, UsersALL, AddUser, DelUser

bot = Bot(token=BotFather, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=MemoryStorage())


@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    if message.from_user.id in admin:
        with sqlite3.connect('database.db') as con:
            cur = con.cursor()
            cur.execute('INSERT OR IGNORE INTO user_id (user_id, status) VALUES (?, 0)', (message.from_user.id,))
            con.commit()
    with sqlite3.connect('database.db') as con:
        cur = con.cursor()
        cur.execute('SELECT user_id FROM user_id WHERE user_id = ?', (message.from_user.id,))
        existing_user = cur.fetchone()

    if existing_user:
        await bot.send_sticker(chat_id=message.from_user.id,
                               sticker='CAACAgIAAxkBAAEJD5Bka3F-fGGis4dzCbojsEqU7vhdVAACfQMAAm2wQgO9Ey75tk26Uy8E',
                               reply_markup=await cmd_starting_(user_id=message.from_user.id))
    else:
        return


@dp.message_handler(commands=['del'])
async def dle(message: types.Message):
    command_parts = message.text.split()
    if len(command_parts) != 2:
        await message.answer('📌Пожалуйста, укажите значение после команды /del.')
        return

    value_to_delete = command_parts[1]
    with sqlite3.connect('database.db') as con:
        cur = con.cursor()
        cur.execute('SELECT ids FROM vk_id WHERE ids = ?', (value_to_delete,))
        existing_id = cur.fetchone()
        if not existing_id:
            await message.answer(f'❌Запись с ID {value_to_delete} не найдена.')
            return

        cur.execute('DELETE FROM vk_id WHERE ids = ?', (value_to_delete,))
        con.commit()

    await message.answer(f'✅Запись с ID {value_to_delete} успешно удалена.')


@dp.message_handler(text='👀Просмотр пользователей')
async def search(message: types.Message):
    text = '<b>📋Список ID:</b>\n'
    result = await check_user(message.from_user.id)
    online_list = []
    offline_list = []
    for i in result:
        if i.startswith('✅'):
            online_list.append(i)
        else:
            offline_list.append(i)
    text += '\n'.join(online_list) + '\n'
    text += '\n'.join(offline_list) + '\n'

    await message.answer(text, reply_markup=await send_opovos(user_id=message.from_user.id))


@dp.callback_query_handler(lambda x: x.data == 'yes')
async def change(callback: types.CallbackQuery):
    with sqlite3.connect('database.db') as con:
        cur = con.cursor()
        cur.execute('UPDATE user_id SET status = ? WHERE user_id = ?', (0, callback.from_user.id))
        con.commit()
        markup = InlineKeyboardMarkup()
        m1 = InlineKeyboardButton('Оповещение ❌', callback_data='no')
        markup.add(m1)
        text = '<b>📋Список ID:</b>\n'
        result = await check_user(callback.from_user.id)
        online_list = []
        offline_list = []
        for i in result:
            if i.startswith('✅'):
                online_list.append(i)
            else:
                offline_list.append(i)
        text += '\n'.join(online_list) + '\n'
        text += '\n'.join(offline_list) + '\n'

        await bot.edit_message_text(reply_markup=markup, message_id=callback.message.message_id,
                                    chat_id=callback.from_user.id, text=text
                                    )


@dp.callback_query_handler(lambda x: x.data == 'no')
async def change(callback: types.CallbackQuery):
    with sqlite3.connect('database.db') as con:
        cur = con.cursor()
        cur.execute('UPDATE user_id SET status = ? WHERE user_id = ?', (1, callback.from_user.id))
        con.commit()
        markup = InlineKeyboardMarkup()
        m1 = InlineKeyboardButton('Оповещение ✅', callback_data='yes')
        markup.add(m1)
        text = '<b>📋Список ID:</b>\n'
        result = await check_user(callback.from_user.id)
        online_list = []
        offline_list = []
        for i in result:
            if i.startswith('✅'):
                online_list.append(i)
            else:
                offline_list.append(i)
        text += '\n'.join(online_list) + '\n'
        text += '\n'.join(offline_list) + '\n'

        await bot.edit_message_text(reply_markup=markup, message_id=callback.message.message_id,
                                    chat_id=callback.from_user.id, text=text
                                    )


@dp.message_handler(text='✏Добавить по штучно')
async def add_user(message: types.Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    m1 = KeyboardButton('❌Отмена')
    markup.add(m1)
    await message.answer('✏️Введите ID пользователя', reply_markup=markup)
    await Users.text.set()


@dp.message_handler(state=Users.text)
async def add(message: types.Message, state: FSMContext):
    if message.text == '❌Отмена':
        await message.answer('❌Отменил', reply_markup=await cmd_starting_(user_id=message.from_user.id))
        await state.finish()
        return

    match = re.match(r'[iI][dD](\d+)', message.text)
    if match:
        id_user = int(match.group(1))
        with sqlite3.connect('database.db') as con:
            cur = con.cursor()
            cur.execute('SELECT ids FROM vk_id WHERE ids = ? AND user_id = ?', (id_user, message.from_user.id))
            existing_id = cur.fetchone()
            print(existing_id)
            if existing_id:
                await message.answer(f'🔁ID <code>{id_user}</code> уже существует в базе',
                                     reply_markup=await cmd_starting_(user_id=message.from_user.id))
            cur.execute('INSERT INTO vk_id (ids, off, user_id) VALUES (?, 1, ?)', (id_user, message.from_user.id))
            con.commit()
        await message.answer(f'✅ID {id_user} успешно добавлен в базу',
                             reply_markup=await cmd_starting_(user_id=message.from_user.id))
    else:
        await message.answer('✏️Введите ID в формате idXXX, где XXX - числовая часть', reply_markup=await cmd_starting_(user_id=message.from_user.id))

    await state.finish()


@dp.message_handler(text='🗑Удалить все ID')
async def deletes(message: types.Message):
    await message.answer('✏Вы уверены что хотите удалить все ID?', reply_markup=await delet())


@dp.callback_query_handler(lambda x: x.data == 'delete_all')
async def all_delete(callback: types.CallbackQuery):
    await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)
    with sqlite3.connect('database.db') as con:
        cur = con.cursor()
        cur.execute('DELETE FROM vk_id WHERE user_id = ?', (callback.from_user.id,))
        con.commit()

    await bot.send_message(chat_id=callback.from_user.id, text='✅Успешно удалил все ID из базы')


@dp.message_handler(text='✏Добавить списком')
async def add_spisok(message: types.Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    m1 = KeyboardButton('❌Отмена')
    markup.add(m1)
    await message.answer('❕Введите список ID обязательно через строку', reply_markup=markup)
    await UsersALL.text.set()


@dp.message_handler(state=UsersALL.text)
async def add(message: types.Message, state: FSMContext):
    if message.text == '❌Отмена':
        await message.answer('❌Отменил', reply_markup=await cmd_starting_(user_id=message.from_user.id))
        await state.finish()
        return

    split = message.text.split('\n')
    down = []
    with sqlite3.connect('database.db') as con:
        cur = con.cursor()
        for value in split:
            value = value.strip()
            match = re.match(r'[iI][dD](\d+)', value)
            if match:
                id_user = int(match.group(1))
                cur.execute('SELECT ids FROM vk_id WHERE ids = ? AND user_id = ?', (id_user, message.from_user.id))
                existing_id = cur.fetchone()
                if existing_id:
                    await message.answer(f'🔁ID <code>id{id_user}</code> уже существует в базе',
                                         reply_markup=await cmd_starting_(user_id=message.from_user.id))
                cur.execute('INSERT INTO vk_id (ids, off, user_id) VALUES (?, 1, ?)', (id_user, message.from_user.id))
                con.commit()
                down.append(id_user)
            else:
                await message.answer(f'❌Значение "<code>id{value}</code>" не является правильным форматом ID',
                                     reply_markup=await cmd_starting_(user_id=message.from_user.id))

    if down:
        success_message = f'✅ID успешно добавлены в базу:\n\n'
        success_message += '\n'.join(f'<code>id{str(id)}</code>' for id in down)
        await message.answer(success_message,
                             reply_markup=await cmd_starting_(user_id=message.from_user.id))
    await state.finish()

@dp.message_handler(text='💠Добавить пользователя')
async def add_user(message: types.Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    m1 = KeyboardButton('❌Отмена')
    markup.add(m1)
    await message.answer('✏️Введите ID пользователя', reply_markup=markup)
    await AddUser.text.set()


@dp.message_handler(state=AddUser.text)
async def vvod(message: types.Message, state: FSMContext):
    if message.text == '❌Отмена':
        await message.answer('❌Отменил', reply_markup=await cmd_starting_(user_id=message.from_user.id))
        await state.finish()
        return
    if not message.text.isdigit():
        await message.answer('✏️Введите ID в числовом формате')
        return

    id_user = int(message.text)
    with sqlite3.connect('database.db') as con:
        cur = con.cursor()
        cur.execute('SELECT user_id FROM user_id WHERE user_id = ?', (id_user,))
        existing_user = cur.fetchone()
        if existing_user:
            await message.answer(f'⚠️Пользователь с ID <code>{id_user}</code> уже существует в базе данных',
                                 reply_markup=await cmd_starting_(user_id=message.from_user.id))
            await state.finish()
            return
        cur.execute('INSERT INTO user_id (user_id, status) VALUES (?, 0)', (id_user,))
        con.commit()
    await state.finish()
    await message.answer(f'✅Успешно добавил пользователя с ID: <code>{id_user}</code>', reply_markup=await cmd_starting_(user_id=message.from_user.id))


@dp.message_handler(text='👻Удалить пользователя')
async def add_user(message: types.Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    m1 = KeyboardButton('❌Отмена')
    markup.add(m1)
    await message.answer('✏️Введите ID пользователя', reply_markup=markup)
    await DelUser.text.set()


@dp.message_handler(state=DelUser.text)
async def vvod(message: types.Message, state: FSMContext):
    if message.text == '❌Отмена':
        await message.answer('❌Отменил', reply_markup=await cmd_starting_(user_id=message.from_user.id))
        await state.finish()
        return
    if not message.text.isdigit():
        await message.answer('✏️Введите ID в числовом формате')
        return

    id_user = int(message.text)
    with sqlite3.connect('database.db') as con:
        cur = con.cursor()
        cur.execute('SELECT user_id FROM user_id WHERE user_id = ?', (id_user,))
        existing_user = cur.fetchone()
        if not existing_user:
            await message.answer(f'🔍Пользователь с ID <code>{id_user}</code> не найден',
                                 reply_markup=await cmd_starting_(user_id=message.from_user.id))
            await state.finish()
            return
        cur.execute('DELETE FROM user_id WHERE user_id = ?', (id_user,))
        con.commit()
    await state.finish()
    await message.answer(f'✅Успешно удален пользователь с ID: <code>{id_user}</code>', reply_markup=await cmd_starting_(user_id=message.from_user.id))


async def monitor_online(id_user):
    print(id_user)
    async with aiohttp.ClientSession() as session:
        device = ["с мобильного", "с iPhone", "с iPad", "с Android", "с Windows Phone", "с Windows 10", "с ПК",
                  "с VK Mobile"]

        with sqlite3.connect('database.db') as con:
            cur = con.cursor()
            cur.execute('SELECT ids FROM vk_id')
            rows = cur.fetchall()

        user_ids = ",".join(str(e[0]) for e in rows)
        get_link = f"https://api.vk.com/method/users.get?user_ids={user_ids}&fields=sex,online,last_seen&access_token={vk_api}&v=5.85&lang=ru"

        async with session.get(get_link) as response:
            json = await response.json()

            for userinfo in json["response"]:
                try:
                    userstat = userinfo["last_seen"]
                    user_id = userinfo["id"]
                except:
                    continue
                ms_time = time.gmtime(int(userstat["time"]) + 10800)
                try:
                    if userinfo['online'] == 1:
                        with sqlite3.connect('database.db') as con:
                            cur = con.cursor()
                            cur.execute('SELECT off FROM vk_id WHERE ids = ? AND user_id = ?', (user_id, id_user))
                            naf = cur.fetchone()
                            if int(naf[0]) == 1:
                                nameofuser = userinfo["first_name"] + " " + userinfo["last_name"]
                                await bot.send_message(
                                    text=f'✅ {nameofuser} <code>id{user_id}</code> {device[int(userstat["platform"]) - 1]}',
                                    chat_id=int(id_user))
                                cur.execute('UPDATE vk_id SET off = ? WHERE ids = ?', (0, user_id))
                                con.commit()
                except:
                    continue


async def monitor_users():
    while True:
        with sqlite3.connect('database.db') as con:
            cur = con.cursor()
            cur.execute('SELECT user_id FROM user_id WHERE status = 1')
            users = cur.fetchall()
        async with aiohttp.ClientSession() as session:
            for user in users:
                user_id = user[0]
                await monitor_online(user_id)

        await asyncio.sleep(10)


async def start_monitoring():
    loop = asyncio.get_event_loop()
    loop.create_task(monitor_users())


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    loop = asyncio.get_event_loop()
    loop.create_task(start_monitoring())
    executor.start_polling(dp, loop=loop, skip_updates=True)
