from aiogram.dispatcher.filters.state import StatesGroup, State


class Users(StatesGroup):
    text = State()


class UsersALL(StatesGroup):
    text = State()


class AddUser(StatesGroup):
    text = State()

class DelUser(StatesGroup):
    text = State()
