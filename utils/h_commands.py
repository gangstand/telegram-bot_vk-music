from os import path
from shutil import rmtree

from aiogram import types
from core.settings import dp
from utils.button import markup_exit, markup_music, markup_auth
from core.variables import (
    HCOM_WEL,
    HCOM_AUT_EXIT,
    HCOM_AUT_MUSIC,
    HCOM_AUT_NOMUSIC,
    HCOM_NOWEL,
    HCOM_EXIT
)


@dp.message_handler(commands='start')
async def start(message: types.Message):
    await message.answer(HCOM_WEL)

    username = message.from_user.first_name

    if path.exists(f'{username}/vk_config.v2.json'):
        await message.answer(HCOM_AUT_EXIT, reply_markup=markup_exit)

        if path.exists(f'{username}/music_list.txt'):
            await message.answer(HCOM_AUT_MUSIC, reply_markup=markup_music)
        else:
            return await message.answer(HCOM_AUT_NOMUSIC)
    else:
        return await message.answer(HCOM_NOWEL, reply_markup=markup_auth)


@dp.callback_query_handler(lambda c: c.data == 'Exit')
async def exit(message: types.Message):
    username = message.from_user.first_name
    rmtree(f"{username}")
    return await message.answer(HCOM_EXIT)
