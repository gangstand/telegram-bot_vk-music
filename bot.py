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

bot = Bot(token="5554601137:AAFRyVxyEusP4YmolVV2Tp6Kd1P29J8MW7c")
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

        print(password, key)

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
                    await message.answer('Список музыки загружены (Чтобы обновить список, нужно перезайти в сервис!)',
                                         reply_markup=markup_music)
            except:
                await message.answer(
                    'Список музыки не загружены, ожидайте он загружается...\nВремя загрузки зависит от размера вашего плейлиста')
            for track in vkaudio.get_iter():
                with open("music_list.txt", "a", encoding="utf8") as f:
                    print(track, file=f)
                    f.close()
            await message.answer('Список музыки загружен :D\n(Чтобы обновить список, нужно перезайти в сервис)',
                                 reply_markup=markup_music)
        except vk_api.AuthError as error_msg:
            await message.answer(error_msg)


class Filter(StatesGroup):
    id = State()


@dp.callback_query_handler(lambda c: c.data == 'Music_id')
async def Save_new_massage(callback_query: types.CallbackQuery):
    await Filter.id.set()
    await bot.send_message(callback_query.from_user.id, 'Введите id песни:')


@dp.message_handler(state=Filter.id)
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
            print(title)
            music_url = line.split()[8].replace("'", '').replace(",", '')
            print(music_url)
            title = re.sub("[|(|)|'|,|]", "", str(title)).replace('title', '').replace('"', '').replace('[','').replace(']','')
            title_ = title.replace(" ", "_").replace(".", "_").replace(":", "_")
            await bot.send_message(message.from_user.id, f'Песня - {title}')
            await bot.send_message(message.from_user.id, 'Компилирую и отправляю...')
            os.system(f'ffmpeg -y -i {music_url} -vn -ar 44100 -ac 2 -ab 192 -f mp3 -c copy music\\{title_}.mp3')
            music_out = open(f"music/{title_}.mp3", "rb")
            await bot.send_document(message.from_user.id, music_out)
        x += 1


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
