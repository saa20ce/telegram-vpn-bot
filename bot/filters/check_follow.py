from aiogram.filters import Filter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.misc.language import get_lang, Localization
from bot.misc.util import CONFIG

_ = Localization.text


class IsSub(Filter):
    def __init__(self):
        self.id_channel = CONFIG.id_channel
        self.link_channel = CONFIG.link_channel

    async def __call__(self, message: Message, state: FSMContext) -> bool:
        self.lang = await get_lang(message.from_user.id, state)
        if await self.check_subs(message.from_user.id, message.bot):
            return True
        await message.answer(
            _('no_follow', self.lang),
            reply_markup=await self.follow_channel()
        )
        return False

    async def check_subs(self, user_telegram_id, bot):
        user_channel_status = await bot.get_chat_member(
            chat_id=f'-100{self.id_channel}',
            user_id=user_telegram_id
        )
        return user_channel_status.status != 'left'

    async def follow_channel(self) -> InlineKeyboardMarkup:
        kb = InlineKeyboardBuilder()
        kb.button(text=_('no_follow_button', self.lang), url=self.link_channel)
        kb.adjust(1)
        return kb.as_markup()

