from os import environ
from typing import Final

from bot.misc.util import CONFIG


class TgKeys:
    TOKEN: Final = CONFIG.tg_token or environ.get('TOKEN', 'define me!')
