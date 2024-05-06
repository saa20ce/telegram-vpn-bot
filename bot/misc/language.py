import gettext
from dataclasses import dataclass
from pathlib import Path

from aiogram.fsm.context import FSMContext

from bot.database.methods.get import get_person_lang
from bot.misc.util import CONFIG


async def get_lang(user_id, state: FSMContext=None):
    if state is not None:
        data = await state.get_data()
        lang = data.get('lang')
        if lang is None:
            lang = await get_person_lang(user_id)
            await state.update_data(lang=lang)
        return lang
    else:
        return await get_person_lang(user_id)


@dataclass
class Localization:
    ALL_Languages = {
        'en': 'English 🇬🇧',
        'ru': 'Русский 🇷🇺'
    }
    PATH = Path(__file__).resolve().parent.parent / 'locale'

    @classmethod
    def get_reply_button(cls, key_text) -> list:
        buttons_text = []
        for lang_key in cls.ALL_Languages.keys():
            lang = gettext.translation(
                'bot',
                localedir=cls.PATH,
                languages=[lang_key]
            )
            lang.install()
            buttons_text.append(lang.gettext(key_text))
        return buttons_text

    @classmethod
    def text(cls, key_text, language=CONFIG.languages):
        lang = gettext.translation(
            'bot',
            localedir=cls.PATH,
            languages=[language]
        )
        lang.install()
        return lang.gettext(key_text)
