from aiogram.filters import Filter
from aiogram.types import Message
from bot.misc.util import CONFIG


class IsAdmin(Filter):
    def __init__(self):
        config = CONFIG
        self.id_admin = config.admin_tg_id

    async def __call__(self, message: Message) -> bool:
        return message.from_user.id == self.id_admin
