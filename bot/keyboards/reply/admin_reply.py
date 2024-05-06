from aiogram.types import ReplyKeyboardMarkup, KeyboardButton as keyBtn
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from bot.misc.language import Localization

_ = Localization.text


async def admin_menu(lang) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.row(
        keyBtn(text=_('admin_users_btn', lang)),
        keyBtn(text=_('admin_promo_btn', lang))
    )
    kb.row(
        keyBtn(text=_('admin_servers_btn', lang)),
        keyBtn(text=_('admin_reff_system_btn', lang))
    )
    kb.row(keyBtn(text=_('admin_send_message_users_btn', lang)))
    kb.row(keyBtn(text=_('back_general_menu_btn', lang)))
    return kb.as_markup(resize_keyboard=True)


async def admin_user_menu(lang) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.row(keyBtn(text=_('admin_show_statistic_btn', lang)))
    kb.row(keyBtn(text=_('admin_edit_user_btn', lang)))
    kb.row(keyBtn(text=_('admin_static_user_btn', lang)))
    kb.row(keyBtn(text=_('admin_back_admin_menu_btn', lang)))
    return kb.as_markup(resize_keyboard=True)


async def static_user_menu(lang) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.row(keyBtn(text=_('admin_static_add_user_btn', lang)))
    kb.row(keyBtn(text=_('admin_static_show_users_btn', lang)))
    kb.row(keyBtn(text=_('admin_back_users_menu_btn', lang)))
    return kb.as_markup(resize_keyboard=True)


async def back_static_user_menu(lang) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.row(keyBtn(text=_('admin_exit_btn', lang)))
    return kb.as_markup(resize_keyboard=True)


async def show_user_menu(lang) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.row(keyBtn(text=_('admin_statistic_show_all_users_btn', lang)))
    kb.row(
        keyBtn(text=_('admin_statistic_show_sub_users_btn', lang)),
        keyBtn(text=_('admin_statistic_show_payments_btn', lang))
    )
    kb.row(keyBtn(text=_('admin_back_users_menu_btn', lang)))
    return kb.as_markup(resize_keyboard=True)


async def server_menu(lang) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.row(keyBtn(text=_('admin_server_show_all_btn', lang)))
    kb.row(keyBtn(text=_('admin_server_add_btn', lang)))
    kb.row(keyBtn(text=_('admin_server_delete_btn', lang)))
    kb.row(keyBtn(text=_('admin_back_admin_menu_btn', lang)))
    return kb.as_markup(resize_keyboard=True)


async def back_server_menu(lang) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.row(keyBtn(text=_('admin_server_cancellation', lang)))
    return kb.as_markup(resize_keyboard=True)


async def back_user_menu(lang) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.row(keyBtn(text=_('admin_users_cancellation', lang)))
    return kb.as_markup(resize_keyboard=True)


async def back_admin_menu(lang) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.row(keyBtn(text=_('admin_back_admin_menu_btn', lang)))
    return kb.as_markup(resize_keyboard=True)
