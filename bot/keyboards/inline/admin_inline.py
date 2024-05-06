from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.misc.callbackData import (
    ChoosingConnectionMethod,
    ChoosingPanel,
    ServerWork,
    ServerUserList,
    EditUserPanel,
    DeleteTimeClient,
    DeleteStaticUser,
    MissingMessage,
    ChoosingVPN,
    PromocodeDelete,
    AplicationReferral,
    ApplicationSuccess, MessageAdminUser, EditBalanceUser
)
from bot.misc.language import Localization

_ = Localization.text


async def choosing_connection() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(
        text='HTTP 🔌',
        callback_data=ChoosingConnectionMethod(connection=False)
    )
    kb.button(
        text='HTTPS 🔌',
        callback_data=ChoosingConnectionMethod(connection=True)
    )
    kb.adjust(2)
    return kb.as_markup()


async def choosing_vpn() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(
        text='Outline 🪐',
        callback_data=ChoosingVPN(type=0)
    )
    kb.button(
        text='Vless 🐊',
        callback_data=ChoosingVPN(type=1)
    )
    kb.button(
        text='Shadowsocks 🦈',
        callback_data=ChoosingVPN(type=2)
    )
    kb.adjust(1)
    return kb.as_markup()


async def choosing_panel() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(
        text='Sanaei 🖲',
        callback_data=ChoosingPanel(panel='sanaei')
    )
    kb.button(
        text='Alireza 🕹',
        callback_data=ChoosingPanel(panel='alireza')
    )
    kb.adjust(2)
    return kb.as_markup()


async def server_control(work, name_server, lang) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    if work:
        kb.button(
            text=_('not_uses_server_btn', lang),
            callback_data=ServerWork(work=False, name_server=name_server)
        )
    else:
        kb.button(
            text=_('uses_server_btn', lang),
            callback_data=ServerWork(work=True, name_server=name_server)
        )
    kb.button(
        text=_('list_user_server_btn', lang),
        callback_data=ServerUserList(name_server=name_server, action=True)
    )
    kb.button(
        text=_('delete_key_server_btn', lang),
        callback_data=ServerUserList(name_server=name_server, action=False)
    )
    kb.adjust(1)
    return kb.as_markup()


async def edit_client_menu(tgid_user, lang) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(
        text=_('admin_user_add_time_btn', lang),
        callback_data=EditUserPanel(action='add_time')
    )
    kb.button(
        text=_('admin_user_edit_balance_btn', lang),
        callback_data=EditBalanceUser(id_user=tgid_user)
    )
    kb.button(
        text=_('admin_user_message_client_btn', lang),
        callback_data=MessageAdminUser(id_user=tgid_user)
    )
    kb.button(
        text=_('admin_user_delete_time_btn', lang),
        callback_data=EditUserPanel(action='delete')
    )
    kb.adjust(1)
    return kb.as_markup()


async def delete_time_client(lang) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(
        text=_('definitely_dropping_btn', lang),
        callback_data=DeleteTimeClient(delete_time=True)
    )
    kb.adjust(1)
    return kb.as_markup()


async def delete_static_user(name, server, lang) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(
        text=_('delete_static_user_btn', lang),
        callback_data=DeleteStaticUser(name=name, server_name=server)
    )
    kb.adjust(1)
    return kb.as_markup()


async def missing_user_menu(lang) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(
        text=_('admin_user_mailing_all_btn', lang),
        callback_data=MissingMessage(option='all')
    )
    kb.button(
        text=_('admin_user_mailing_sub_btn', lang),
        callback_data=MissingMessage(option='sub')
    )
    kb.button(
        text=_('admin_user_mailing_not_sub_btn', lang),
        callback_data=MissingMessage(option='no')
    )
    kb.button(
        text=_('admin_user_mailing_update_btn', lang),
        callback_data=MissingMessage(option='update')
    )
    kb.adjust(1)
    return kb.as_markup()


async def promocode_menu(lang) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(
        text=_('promo_add_new_btn', lang),
        callback_data='new_promo'
    )
    kb.button(
        text=_('promo_show_all_btn', lang),
        callback_data='show_promo'
    )
    kb.adjust(1)
    return kb.as_markup()


async def application_referral_menu(lang) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(
        text=_('applications_show_all_btn', lang),
        callback_data=AplicationReferral(type=True)
    )
    kb.button(
        text=_('applications_show_active_btn', lang),
        callback_data=AplicationReferral(type=False)
    )
    kb.adjust(1)
    return kb.as_markup()


async def promocode_delete(id_promo, mes_id, lang) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(
        text=_('delete_static_user_btn', lang),
        callback_data=PromocodeDelete(id_promo=id_promo, mes_id=mes_id)
    )
    kb.adjust(1)
    return kb.as_markup()


async def application_success(
        id_application,
        mes_id,
        lang
) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(
        text=_('applications_success_btn', lang),
        callback_data=ApplicationSuccess(
            id_application=id_application,
            mes_id=mes_id
        )
    )
    kb.adjust(1)
    return kb.as_markup()
