from os import mkdir, path, remove
from shutil import move
from time import sleep
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram import types
from aiogram.dispatcher import FSMContext
from vk_api import vk_api, AuthError
from vk_api.audio import VkAudio

from core.settings import dp, bot
from utils.button import markup_music
from core.variables import HAUTH_LOGIN, HAUTH_PS, HCOM_AUT_MUSIC, HCOM_AUT_NOMUSIC


class FormPS(StatesGroup):
    login = State()
    password = State()


@dp.callback_query_handler(lambda c: c.data == 'Enter')
async def enter(callback_query: types.CallbackQuery):
    await FormPS.login.set()
    await bot.send_message(callback_query.from_user.id, HAUTH_LOGIN)


@dp.message_handler(state=FormPS.login)
async def login(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['login'] = message.text
        await FormPS.next()
        await message.answer(HAUTH_PS)


@dp.message_handler(state=FormPS.password)
async def password(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['password'] = message.text
        username = message.from_user.first_name
        await state.finish()

        if not path.exists(username):
            mkdir(username)

        try:
            password_vk, key_handler = data['password'].split()
        except ValueError:
            password_vk = data['password']

    def auth_handler():
        remember_device = True
        return key_handler, remember_device

    def captcha_handler(captcha):
        key = input("Enter captcha code {0}: ".format(captcha.get_url())).strip()
        return captcha.try_again(key)

    vk_session = vk_api.VkApi(
        data['login'],
        password_vk,
        auth_handler=auth_handler,
        captcha_handler=captcha_handler
    )

    try:
        vk_session.auth()
        vkaudio = VkAudio(vk_session)
        sleep(3)
        source_path = "vk_config.v2.json"
        if path.exists(source_path):
            destination_path = username
            move(source_path, destination_path)

        if path.exists(f'{username}/music_list.txt'):
            remove(f"{username}/music_list.txt")

        await message.answer("Вы успешно вошли")

        if path.exists(f'{username}/music_list.txt'):
            await message.answer(HCOM_AUT_MUSIC, reply_markup=markup_music)
        else:
            return await message.answer(HCOM_AUT_NOMUSIC)

        for track in vkaudio.get_iter():
            with open(f"{username}/music_list.txt", "a", encoding="utf8") as f:
                print(f"{track.get('url')}___{track.get('artist')} : {track.get('title')}", file=f)

        await message.answer(HCOM_AUT_NOMUSIC, reply_markup=markup_music)

    except AuthError as error:
        await message.answer(error)
