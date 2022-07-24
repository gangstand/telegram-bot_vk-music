import os

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from core.settings import dp, bot
from core.variables import HSR_MUSIC, H_MUSIC_RD


class FilterSearch(StatesGroup):
    search = State()


@dp.callback_query_handler(lambda c: c.data == 'Music_search')
async def music_search(callback_query: types.CallbackQuery):
    await FilterSearch.search.set()
    await bot.send_message(callback_query.from_user.id, HSR_MUSIC)


@dp.message_handler(state=FilterSearch.search)
async def music_search_save(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['id'] = message.text
        search_string = data['id']
        username = message.from_user.first_name
        await state.finish()

        with open(f"{username}/music_list.txt", "r", encoding='utf8') as f:
            n = 0
            for line in f:
                n += 1
                if search_string in line:

                    f = open(f"{username}/music_list.txt", "r", encoding='utf8')
                    x = 1
                    id_music = n

                    for line in f:
                        if x == id_music:

                            url, title = line.split("___")
                            _title = title.replace(":", "_").replace("?", "_").replace(" ", "_")

                            await bot.send_message(message.from_user.id, f'Песня - {title}')
                            try:
                                music_out = open(f"music\\{_title}.mp3", "rb")
                                await bot.send_document(message.from_user.id, music_out)
                                music_out.close()
                            except:
                                os.system(f'streamlink --output music\\{_title}.ts {url} best')
                                os.system(f'ffmpeg -y -i music\\{_title}.ts music\\{_title}.mp3')
                                music_out = open(f"music\\{_title}.mp3", "rb")
                                await bot.send_document(message.from_user.id, music_out)
                                music_out.close()
                        x += 1
                    f.close()
        f.close()
    await bot.send_message(message.from_user.id, H_MUSIC_RD)
