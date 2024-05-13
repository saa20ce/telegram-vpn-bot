import time
from datetime import datetime

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton as keyBtn
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from bot.misc.language import Localization
from bot.misc.util import CONFIG

_ = Localization.text


async def user_menu(person, lang) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    time_sub = datetime.utcfromtimestamp(
        int(person.subscription) + CONFIG.UTC_time * 3600).strftime(
        '%d.%m.%Y %H:%M')
    time_now = int(time.time())
    if int(person.subscription) >= time_now:
        kb.add(keyBtn(
            text=_('subscription_time_btn', lang).format(time=time_sub))
        )
    else:
        kb.button(
            text=_('subscription_not_time_btn', lang).format(time=time_sub)
        )
    kb.row(
        keyBtn(text=_('subscription_btn', lang)),
        keyBtn(text=_('vpn_connect_btn', lang))
    )
    kb.row(
        keyBtn(text=_('affiliate_btn', lang)),
        keyBtn(text=_('bonus_btn', lang))
    )
    kb.row(
        keyBtn(text=_('about_vpn_btn', lang)),
        keyBtn(text=_('language_btn', lang))
    )
    if CONFIG.admin_tg_id == person.tgid:
        kb.row(keyBtn(text=_('admin_panel_btn', lang)))

    return kb.as_markup(resize_keyboard=True)


async def subscription_menu(lang, has_used_trial) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.row(
        keyBtn(text=_('balanced_btn', lang)),
        keyBtn(text=_('to_extend_btn', lang))
    )
    if not has_used_trial:
        kb.row(keyBtn(text=_('trial_period_btn', lang)))
    kb.row(keyBtn(text=_('back_general_menu_btn', lang)))
    return kb.as_markup(resize_keyboard=True)


async def balance_menu(person, lang) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.row(keyBtn(
        text=_('balance_user_btn', lang).format(balance=person.balance))
    )
    kb.row(keyBtn(text=_('replenish_bnt', lang)))
    kb.row(keyBtn(text=_('back_subscription_menu_btn', lang)))
    return kb.as_markup(resize_keyboard=True)


async def back_menu(lang) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.row(keyBtn(text=_('back_general_menu_btn', lang)))
    return kb.as_markup(resize_keyboard=True)


async def back_menu_balance(lang) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.row(keyBtn(text=_('back_balance_menu_btn', lang)))
    return kb.as_markup(resize_keyboard=True)
