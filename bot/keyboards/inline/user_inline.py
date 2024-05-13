from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.misc.callbackData import (
    ChoosingMonths,
    ChoosingPrise,
    ChoosingPyment,
    ChooseServer,
    MessageAdminUser, ChoosingLang
)
from bot.misc.language import Localization
from bot.misc.util import CONFIG

_ = Localization.text


# async def replenishment(config, lang) -> InlineKeyboardMarkup:
#     kb = InlineKeyboardBuilder()
#     if config.tg_wallet_token != "":
#         kb.button(
#             text=_('payments_wallet_pay_btn', lang),
#             callback_data=ChoosingPyment(payment='WalletPay'))
#     if config.yookassa_shop_id != "" and config.yookassa_secret_key != "":
#         kb.button(
#             text=_('payments_yookassa_btn', lang),
#             callback_data=ChoosingPyment(payment='KassaSmart'))
#     if config.yoomoney_token != "" and config.yoomoney_wallet_token != "":
#         kb.button(
#             text=_('payments_yoomoney_btn', lang),
#             callback_data=ChoosingPyment(payment='YooMoney'))
#     if config.lava_token_secret != "" and config.lava_id_project != "":
#         kb.button(
#             text=_('payments_lava_btn', lang),
#             callback_data=ChoosingPyment(payment='Lava'))
#     if (
#             config.yookassa_shop_id == ""
#             and config.tg_wallet_token == ""
#             and config.yoomoney_token == ""
#             and config.lava_token_secret == ""
#     ):
#         kb.button(text=_('payments_not_btn_1', lang), callback_data='none')
#         kb.button(text=_('payments_not_btn_2', lang), callback_data='none')
#     kb.adjust(1)
#     return kb.as_markup()

async def replenishment(config, lang, is_trial=False) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    payment_methods = {
        'WalletPay': config.tg_wallet_token,
        'KassaSmart': (config.yookassa_shop_id and config.yookassa_secret_key),
        'YooMoney': (config.yoomoney_token and config.yoomoney_wallet_token),
        'Lava': (config.lava_token_secret and config.lava_id_project)
    }

    for method, available in payment_methods.items():
        if available:
            callback_data = ChoosingPyment(payment=method, is_trial=is_trial)
            text = _('payments_' + method.lower() + '_btn', lang)
            kb.button(text=text, callback_data=callback_data)

    if all(not v for v in payment_methods.values()):
        kb.button(text=_('payments_not_btn_1', lang), callback_data='none')
        kb.button(text=_('payments_not_btn_2', lang), callback_data='none')
    
    kb.adjust(1)
    return kb.as_markup()


async def deposit_amount(CONGIG) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for deposit in CONGIG.deposit:
        kb.button(text=f'{deposit} ₽', callback_data='Rub')
    kb.adjust(1)
    return kb.as_markup()


async def renew(CONGIG, lang) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    months = {1: 0, 3: 1, 6: 2}
    for month, price in months.items():
        kb.button(
            text=_('to_extend_month_btn', lang)
            .format(count_month=month, price=CONGIG.month_cost[price]),
            callback_data=ChoosingMonths(
                price=str(CONGIG.month_cost[price]),
                month_count=month
            )
        )
    kb.adjust(1)
    return kb.as_markup()


async def price_menu(CONGIG, payment) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for price in CONGIG.deposit:
        kb.button(
            text=f'{price} ₽',
            callback_data=ChoosingPrise(
                price=int(price),
                payment=payment
            )
        )
    kb.adjust(1)
    return kb.as_markup()


async def wallet_pay(order, lang) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text='👛 Pay via Wallet', url=order.pay_link)
    kb.button(
        text=_('instruction_payment_btn', lang),
        url=_('instruction_walletpay', lang)
    )
    kb.adjust(1)
    return kb.as_markup()


async def choosing_lang() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for lang, cls in Localization.ALL_Languages.items():
        kb.button(text=cls, callback_data=ChoosingLang(lang=lang))
    kb.adjust(1)
    return kb.as_markup()


async def pay_and_check(link_invoice: str, lang) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=_('user_pay_sub_btn', lang), url=link_invoice)
    kb.adjust(1)
    return kb.as_markup()


async def instruction_manual(type_vpn, lang) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    if type_vpn == 0:
        iphone = _('instruction_iphone_outline', lang)
        android = _('instruction_android_outline', lang)
        windows = _('instruction_windows_outline', lang)
    elif type_vpn == 1 or type_vpn == 2:
        iphone = _('instruction_iphone_vless', lang)
        android = _('instruction_android_vless', lang)
        windows = _('instruction_windows_vless', lang)
    else:
        raise Exception(f'The wrong type VPN - {type_vpn}')
    kb.button(text=_('instruction_use_iphone_btn', lang), url=iphone)
    kb.button(text=_('instruction_use_android_btn', lang), url=android)
    kb.button(text=_('instruction_use_pc_btn', lang), url=windows)
    kb.button(text=_('instruction_check_vpn_btn', lang), url='https://2ip.ru/')
    kb.adjust(1)
    return kb.as_markup()


async def share_link(ref_link, lang, ref_balance=None) -> InlineKeyboardMarkup:
    link = f'https://t.me/share/url?url={ref_link}'
    kb = InlineKeyboardBuilder()
    kb.button(text=_('user_share_btn', lang), url=link)
    if ref_balance is not None:
        if ref_balance >= CONFIG.minimum_withdrawal_amount:
            kb.button(
                text=_('withdraw_funds_btn', lang),
                callback_data='withdrawal_of_funds'
            )
        else:
            kb.button(
                text=_('enough_funds_withdraw_btn', lang),
                callback_data='none'
            )
    kb.button(
        text=_('write_the_admin_btn', lang),
        callback_data='message_admin'
    )
    kb.adjust(1)
    return kb.as_markup()


async def promo_code_button(lang) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=_('write_the_promo_btn', lang), callback_data='promo_code')
    kb.adjust(1)
    return kb.as_markup()


async def choose_server(all_server, active_server_id) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for server in all_server:
        text_button = \
            f'🟢{ server.name }🟢' \
            if server.id == active_server_id \
            else server.name
        kb.button(
            text=text_button,
            callback_data=ChooseServer(id_server=server.id)
        )
    kb.adjust(1)
    return kb.as_markup()


async def message_admin_user(tgid_user, lang) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(
        text=_('admin_user_send_reply_btn', lang),
        callback_data=MessageAdminUser(id_user=tgid_user)
    )
    kb.adjust(1)
    return kb.as_markup()
