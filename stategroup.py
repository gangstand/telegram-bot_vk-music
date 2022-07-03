from aiogram.dispatcher.filters.state import StatesGroup, State


class Form(StatesGroup):
    login = State()
    password = State()


class FilterId(StatesGroup):
    id = State()


class FilterSearch(StatesGroup):
    search = State()
