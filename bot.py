from aiogram.utils import executor
from core.settings import dp
from utils.h_commands import start, exit
from utils.h_auth_vk import enter, login, password
from utils.h_quantity_music import music_quantity
from utils.h_id_music import music_id, music_id_save
from utils.h_search_music import music_search, music_search_save

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
