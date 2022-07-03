from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

Enter = InlineKeyboardButton('Войти', callback_data='Enter')
Exit = InlineKeyboardButton('Выйти', callback_data='Exit')

markup_exit = InlineKeyboardMarkup().add(Exit)
markup_auth = InlineKeyboardMarkup().add(Enter)

Music_quantity = InlineKeyboardButton('Количество музыки', callback_data='Music_quantity')
Music_id = InlineKeyboardButton('Поиск музыки по id', callback_data='Music_id')
Music_search = InlineKeyboardButton('Поиск музыки по названию', callback_data='Music_search')
markup_music = InlineKeyboardMarkup().add(Music_quantity).add(Music_id).add(Music_search)
