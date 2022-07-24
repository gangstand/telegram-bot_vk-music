from aiogram import types

from core.settings import bot, dp


@dp.callback_query_handler(lambda c: c.data == 'Music_quantity')
async def music_quantity(callback_query: types.CallbackQuery):
    username = callback_query.from_user.first_name
    with open(f'{username}/music_list.txt', encoding='utf8') as f:
        quantity = sum(1 for line in f)
    await bot.send_message(callback_query.from_user.id, f"{quantity} музыки")
