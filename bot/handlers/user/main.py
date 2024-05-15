import logging

from aiogram import Router, F
from aiogram import types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.utils.payload import decode_payload

from bot.misc.util import CONFIG
from .referral_user import referral_router
from .payment_user import callback_user

from bot.database.methods.get import (
    get_person,
    get_server_id,
    get_free_servers
)
from bot.database.methods.insert import add_new_person
from bot.database.methods.update import (
    person_delete_server,
    add_user_in_server,
    server_space_update, add_time_person, update_lang
)
from bot.keyboards.inline.user_inline import (
    replenishment,
    renew,
    instruction_manual,
    choose_server,
    choosing_lang
)
from bot.keyboards.reply.user_reply import (
    user_menu,
    subscription_menu,
    balance_menu
)
from bot.misc.VPN.ServerManager import ServerManager
from bot.misc.language import Localization, get_lang
from bot.misc.callbackData import ChooseServer, ChoosingLang

log = logging.getLogger(__name__)


_ = Localization.text
btn_text = Localization.get_reply_button

user_router = Router()
user_router.include_routers(callback_user, referral_router)


@user_router.message(Command("start"))
async def command(m: Message, state: FSMContext, command: Command = None):
    lang = await get_lang(m.from_user.id, state)
    await state.clear()
    if not await get_person(m.from_user.id):
        try:
            user_name = f'@{str(m.from_user.username)}'
        except Exception as e:
            log.error(e)
            user_name = str(m.from_user.username)
        reference = decode_payload(command.args) if command.args else None
        if reference is not None:
            if reference != str(m.from_user.id):
                await give_bonus_invitee(m, reference, lang)
            else:
                await m.answer(_('referral_error', lang))
                reference = None
        await add_new_person(
            m.from_user,
            user_name,
            CONFIG.trial_period,
            reference
        )
        await m.answer(_('hello_message', lang).format(name_bot=CONFIG.name))
        await m.answer(_('trial_message', lang))
    person = await get_person(m.from_user.id)
    await m.answer(
        _('main_message', lang),
        reply_markup=await user_menu(person, lang)
    )


async def give_bonus_invitee(m, reference, lang):
    await m.bot.send_message(reference, _('referral_new_user', lang))
    await add_time_person(
        reference,
        CONFIG.referral_day*CONFIG.COUNT_SECOND_DAY
    )


@user_router.message(F.text.in_(btn_text('vpn_connect_btn')))
async def choose_server_user(message: Message, state: FSMContext) -> None:
    lang = await get_lang(message.from_user.id, state)
    try:
        all_active_server = await get_free_servers()
    except Exception as e:
        log.info('Error get free servers:', e, '-- OK')
        await message.answer(_('not_server', lang))
        return
    person = await get_person(message.from_user.id)
    await message.answer(
        _('choosing_connect', lang),
        reply_markup=await choose_server(all_active_server, person.server)
    )


@user_router.message(F.text.in_(btn_text('language_btn')))
async def choose_server_user(message: Message, state: FSMContext) -> None:
    lang = await get_lang(message.from_user.id, state)
    await message.answer(
        _('select_language', lang),
        reply_markup=await choosing_lang()
    )


@user_router.callback_query(ChoosingLang.filter())
async def deposit_balance(
        call: CallbackQuery,
        state: FSMContext,
        callback_data: ChoosingLang
) -> None:
    lang = callback_data.lang
    await update_lang(lang, call.from_user.id)
    await state.update_data(lang=lang)
    person = await get_person(call.from_user.id)
    await call.message.answer(
        _('inform_language', lang),
        reply_markup=await user_menu(person, person.lang)
    )
    await call.answer()


@user_router.callback_query(ChooseServer.filter())
async def connect_vpn(
        call: CallbackQuery,
        callback_data: ChooseServer,
        state: FSMContext
) -> None:
    lang = await get_lang(call.from_user.id, state)
    choosing_server_id = callback_data.id_server
    client = await get_person(call.from_user.id)
    if client.banned:
        await call.message.answer(_('ended_sub_message', lang))
        await call.answer()
        return
    if client.server == choosing_server_id:
        try:
            server = await get_server_id(client.server)
            server_manager = ServerManager(server)
            config = await server_manager.get_key(
                name=call.from_user.id,
                name_key=CONFIG.name
            )
            if config is None:
                raise Exception('Server Not Connected')
        except Exception as e:
            await server_not_found(call.message, e, lang)
            await call.answer()
            return
    else:
        try:
            server = await get_server_id(choosing_server_id)
            if client.server is not None:
                await delete_key_old_server(client.server, call.from_user.id)
        except Exception as e:
            await call.message.answer(_('ended_sub_message', lang))
            log.info(e, 'none server')
            return
        try:
            server_manager = ServerManager(server)
            if await server_manager.add_client(call.from_user.id) is None:
                raise Exception('user/main.py add client error')
            config = await server_manager.get_key(
                call.from_user.id,
                name_key=CONFIG.name
            )
            server_parameters = await server_manager.get_all_user()
            if await add_user_in_server(call.from_user.id, server):
                raise _('error_add_server_client', lang)
            await server_space_update(
                server.name,
                len(server_parameters)
            )
        except Exception as e:
            await person_delete_server(call.from_user.id)
            await server_not_found(call.message, e, lang)
            await call.answer()
            log.error('error get config')
            return
    await call.message.edit_text(f'<code>{config}</code>')
    await call.message.answer(
        _('config_user', lang)
        .format(name_vpn=ServerManager.VPN_TYPES.get(server.type_vpn).NAME_VPN)
    )
    if server.type_vpn == 0:
        connect_message = _('how_to_connect_info_outline', lang)
    elif server.type_vpn == 1 or server.type_vpn == 2:
        connect_message = _('how_to_connect_info_vless', lang)
    else:
        raise Exception(f'The wrong type VPN - {server.type_vpn}')
    await call.message.answer(
        connect_message,
        reply_markup=await instruction_manual(server.type_vpn, lang)
    )
    await call.answer()


async def delete_key_old_server(server_id, user_id):
    server = await get_server_id(server_id)
    server_manager = ServerManager(server)
    await server_manager.delete_client(user_id)


async def server_not_found(m, e, lang):
    await m.answer(_('server_not_connected', lang))
    log.error(e)


@user_router.message(
    (F.text.in_(btn_text('subscription_btn')))
    | (F.text.in_(btn_text('back_subscription_menu_btn')))
)
async def info_subscription(m: Message, state: FSMContext) -> None:
    lang = await get_lang(m.from_user.id, state)
    person = await get_person(m.from_user.id)
    has_used_trial = person.trial_used if hasattr(person, 'trial_used') else False
    await m.answer(
        _('inform_subscription', lang),
        reply_markup=await subscription_menu(lang, has_used_trial)
    )


@user_router.message(
    (F.text.in_(btn_text('balanced_btn')))
    | (F.text.in_(btn_text('back_balance_menu_btn')))
)
async def balance(m: Message, state: FSMContext) -> None:
    lang = await get_lang(m.from_user.id, state)
    person = await get_person(m.from_user.id)
    await m.answer(
        _('balance_message', lang),
        reply_markup=await balance_menu(person, lang)
    )


@user_router.message(F.text.in_(btn_text('replenish_bnt')))
async def deposit_balance(m: Message, state: FSMContext) -> None:
    lang = await get_lang(m.from_user.id, state)
    await m.answer(
        _('method_replenishment', lang),
        reply_markup=await replenishment(CONFIG, lang)
    )


@user_router.message(F.text.in_(btn_text('to_extend_btn')))
async def renew_subscription(m: Message, state: FSMContext) -> None:
    lang = await get_lang(m.from_user.id, state)
    await m.answer(
        _('choosing_month_sub', lang),
        reply_markup=await renew(CONFIG, lang)
    )


@user_router.message(F.text.in_(btn_text('back_general_menu_btn')))
async def back_user_menu(m: Message, state: FSMContext) -> None:
    lang = await get_lang(m.from_user.id, state)
    await state.clear()
    person = await get_person(m.from_user.id)
    await m.answer(
        _('main_message', lang),
        reply_markup=await user_menu(person, lang)
    )


@user_router.message(F.text.in_(btn_text('about_vpn_btn')))
async def info_message_handler(m: Message, state: FSMContext) -> None:
    await m.answer(_('about_message', await get_lang(m.from_user.id, state)))


@user_router.message(F.text.in_(btn_text('trial_period_btn')))
async def handle_trial_payment(m: Message, state: FSMContext) -> None:
    log.debug("Handling trial payment button press")
    lang = await get_lang(m.from_user.id, state)
    person = await get_person(m.from_user.id)
    if not person.trial_used:
        log.debug("Trial period is not used yet")
        await m.answer(
            _('method_replenishment', lang),
            reply_markup=await replenishment(CONFIG, lang, True)
        )
        await update_person_trial_status(m.from_user.id, True)
        await m.answer(_('trial_period_activated', lang))
    else:
        log.debug("Trial period has already been used")
        await m.answer(_('trial_period_already_used', lang))
