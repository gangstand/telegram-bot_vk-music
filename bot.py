from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils import executor
from vk_api.audio import VkAudio
import vk_api
import os
import re

bot = Bot(token="")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class Form(StatesGroup):
    login = State()
    password = State()


Enter = InlineKeyboardButton('Войти', callback_data='Enter')
Exit = InlineKeyboardButton('Выйти', callback_data='Exit')

markup_exit = InlineKeyboardMarkup().add(Exit)
markup_auth = InlineKeyboardMarkup().add(Enter)

Music_quantity = InlineKeyboardButton('Количество музыки', callback_data='Music_quantity')
Music_id = InlineKeyboardButton('Поиск музыки по id', callback_data='Music_id')
Music_search = InlineKeyboardButton('Поиск музыки по названию', callback_data='Music_search')
markup_music = InlineKeyboardMarkup().add(Music_quantity).add(Music_id).add(Music_search)


@dp.message_handler(commands='start')
async def start(message: types.Message):
    await message.answer("Здравствуйте Создатель.")
    try:
        with open('vk_config.v2.json'):
            await message.answer('Вы авторизованы, если хотите выйти ↓', reply_markup=markup_exit)
            try:
                with open('music_list.txt'):
                    await message.answer('Список музыки загружен :D\n(Чтобы обновить список, нужно перезайти в сервис)',
                                         reply_markup=markup_music)
            except:
                await message.answer('Список треков не загружен, ожидайте он загружается...')
    except:
        await message.answer('Вы не авторизованы', reply_markup=markup_auth)


@dp.callback_query_handler(lambda c: c.data == 'Enter')
async def enter(callback_query: types.CallbackQuery):
    await Form.login.set()
    await bot.send_message(callback_query.from_user.id, "Введите логин:")


@dp.callback_query_handler(lambda c: c.data == 'Exit')
async def exit(message: types.Message):
    try:
        os.remove("vk_config.v2.json")
        await message.answer("Вы вышли.")
    except:
        await message.answer("Вы уже вышли.")


@dp.callback_query_handler(lambda c: c.data == 'Music_quantity')
async def enter(callback_query: types.CallbackQuery):
    with open('music_list.txt', encoding='utf8') as f:
        quantity = sum(1 for line in f)
    await bot.send_message(callback_query.from_user.id, f"{quantity} музыки")


@dp.message_handler(state=Form.login)
async def login(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['login'] = message.text
        await Form.next()
        await message.answer(
            "Введите пароль (Если присутствует двухфакторная аутификация, введите код через пробел после пароля!):")


def captcha_handler(captcha):
    key = input("Enter captcha code {0}: ".format(captcha.get_url())).strip()
    return captcha.try_again(key)


@dp.message_handler(state=Form.password)
async def password(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['password'] = message.text
        key = "123123"
        try:
            password, key = data['password'].split()
        except:
            password = data['password']

        def auth_handler():
            remember_device = True
            return key, remember_device

        vk_session = vk_api.VkApi(
            data['login'], password,
            auth_handler=auth_handler, captcha_handler=captcha_handler
        )
        await state.finish()
        try:
            vk_session.auth()
            vkaudio = VkAudio(vk_session)
            try:
                os.remove("music_list.txt")
            except:
                pass
            await message.answer("Вы успешно вошли")
            try:
                with open('music_list.txt'):
                    await message.answer('Список музыки загружен (Чтобы обновить список, нужно перезайти в сервис!)',
                                         reply_markup=markup_music)
            except:
                await message.answer(
                    'Список музыки не загружен, ожидайте он загружается...\nВремя загрузки зависит от размера вашего плейлиста')
            for track in vkaudio.get_iter():
                with open("music_list.txt", "a", encoding="utf8") as f:
                    f.close()
            await message.answer('Список музыки загружен :D\n(Чтобы обновить список, нужно перезайти в сервис)',
                                 reply_markup=markup_music)
        except vk_api.AuthError as error_msg:
            await message.answer(error_msg)


class Filter_id(StatesGroup):
    id = State()


@dp.callback_query_handler(lambda c: c.data == 'Music_id')
async def Save_new_massage(callback_query: types.CallbackQuery):
    await Filter_id.id.set()
    await bot.send_message(callback_query.from_user.id, 'Введите id песни:')


@dp.message_handler(state=Filter_id.id)
async def music(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['id'] = message.text
    f = open("music_list.txt", "r", encoding='utf8')
    x = 1
    id_music = int(data['id'])
    await state.finish()
    for line in f:
        if x == id_music:
            title = (line.split()[10:-2])
            music_url = line.split()[8].replace("'", '').replace(",", '')
            title = re.sub("[|(|)|'|,|]", "", str(title)).replace('title', '').replace('"', '').replace(
                '[', '').replace(']', '')
            title_ = title.replace(" ", "_").replace(".", "_").replace(":", "_").replace(
                "?", "_")
            await bot.send_message(message.from_user.id, f'Песня - {title}')
            try:
                music_out = open(f"music\\{title_}.mp3", "rb")
                await bot.send_document(message.from_user.id, music_out)
            except:
                os.system(f'streamlink --output music\\{title_}.ts {music_url} best')
                os.system(f'ffmpeg -y -i music\\{title_}.ts music\\{title_}.mp3')
                music_out = open(f"music\\{title_}.mp3", "rb")
                await bot.send_document(message.from_user.id, music_out)
        x += 1
    await bot.send_message(message.from_user.id, 'Отправка завершена...')


class Filter_search(StatesGroup):
    search = State()


@dp.callback_query_handler(lambda c: c.data == 'Music_search')
async def Save_new_massage(callback_query: types.CallbackQuery):
    await Filter_search.search.set()
    await bot.send_message(callback_query.from_user.id,
                           'Введите название песни или исполнителя:\n(Не выдаёт результат? Введите в правильном регистре)')


@dp.message_handler(state=Filter_search.search)
async def music(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['id'] = message.text
        search_string = data['id']
        with open("music_list.txt", "r", encoding='utf8') as f:
            n = 0
            for line in f:
                n += 1
                if search_string in line:
                    f = open("music_list.txt", "r", encoding='utf8')
                    x = 1
                    id_music = n
                    await state.finish()
                    for line in f:
                        if x == id_music:
                            title = (line.split()[10:-2])
                            music_url = line.split()[8].replace("'", '').replace(",", '')
                            title = re.sub("[|(|)|'|,|]", "", str(title)).replace('title', '').replace('"', '').replace(
                                '[', '').replace(']', '')
                            title_ = title.replace(" ", "_").replace(".", "_").replace(":", "_").replace(
                                "?", "_")
                            await bot.send_message(message.from_user.id, f'Песня - {title}')
                            try:
                                music_out = open(f"music\\{title_}.mp3", "rb")
                                await bot.send_document(message.from_user.id, music_out)
                            except:
                                os.system(f'streamlink --output music\\{title_}.ts {music_url} best')
                                os.system(f'ffmpeg -y -i music\\{title_}.ts music\\{title_}.mp3')
                                music_out = open(f"music\\{title_}.mp3", "rb")
                                await bot.send_document(message.from_user.id, music_out)
                        x += 1
    await bot.send_message(message.from_user.id, 'Отправка завершена...')


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
