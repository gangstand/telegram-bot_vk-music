import os
import re

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from core.settings import dp, bot
from core.variables import HID_MUSIC, H_MUSIC_RD


class FilterId(StatesGroup):
    id = State()


@dp.callback_query_handler(lambda c: c.data == 'Music_id')
async def music_id(callback_query: types.CallbackQuery):
    await FilterId.id.set()
    await bot.send_message(callback_query.from_user.id, HID_MUSIC)


@dp.message_handler(state=FilterId.id)
async def music_id_save(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['id'] = message.text
        username = message.from_user.first_name
        id_music = int(data['id'])
        await state.finish()

        f = open(f"{username}/music_list.txt", "r", encoding='utf8')

        x = 1
        for line in f:
            if x == id_music:

                url, title = line.split("___")

                _title = re.sub("[$|@|&|?|!|,|.|\n|:| ]", '', title).replace("-", "_")
                print(_title)

                await bot.send_message(message.from_user.id, f'Песня - {title}')

                if os.path.exists(f"music/{_title}.mp3"):
                    music_out = open(f"music/{_title}.mp3", "rb")
                    await bot.send_document(message.from_user.id, music_out)
                    music_out.close()
                else:
                    os.system(f'streamlink --output music/{_title}.ts {url} best')
                    os.system(f'ffmpeg -y -i music/{_title}.ts music/{_title}.mp3')
                    music_out = open(f"music/{_title}.mp3", "rb")
                    os.remove(f'music/{_title}.ts')
                    await bot.send_document(message.from_user.id, music_out)
                    music_out.close()
            x += 1
        f.close()
    await bot.send_message(message.from_user.id, H_MUSIC_RD)
