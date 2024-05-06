import io
import logging

from aiogram import Router, F
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.utils.formatting import Text, Bold, Spoiler, Code

from bot.filters.main import IsAdmin
from bot.database.methods.get import (
    get_all_server,
    get_server,
    get_person_id,
    get_all_user, get_all_subscription, get_no_subscription
)
from bot.database.methods.update import (
    server_work_update,
    server_space_update,
    update_delete_users_server
)
from bot.handlers.admin.referal_admin import referral_router
from bot.handlers.admin.user_management import (
    user_management_router,
    string_user
)
from bot.handlers.admin.state_servers import state_admin_router
from bot.handlers.admin.state_servers import AddServer, RemoveServer
from bot.keyboards.inline.admin_inline import server_control, missing_user_menu
from bot.keyboards.reply.admin_reply import (
    admin_menu,
    server_menu,
    back_server_menu, back_admin_menu
)
from bot.keyboards.reply.user_reply import user_menu
from bot.misc.VPN.ServerManager import ServerManager
from bot.misc.language import Localization, get_lang
from bot.misc.util import CONFIG
from bot.misc.callbackData import ServerWork, ServerUserList, MissingMessage

log = logging.getLogger(__name__)

_ = Localization.text
btn_text = Localization.get_reply_button

admin_router = Router()
admin_router.message.filter(IsAdmin())
admin_router.include_routers(
    user_management_router,
    state_admin_router,
    referral_router
)


class StateMailing(StatesGroup):
    input_text = State()


@admin_router.message(
    (F.text.in_(btn_text('admin_panel_btn'))) |
    (F.text.in_(btn_text('admin_back_admin_menu_btn')))
)
async def admin_panel(message: Message, state: FSMContext) -> None:
    lang = await get_lang(message.from_user.id, state)
    await message.answer(
        _('bot_control', lang),
        reply_markup=await admin_menu(lang)
    )
    await state.clear()


# todo: Server management
@admin_router.message(
    F.text.in_(btn_text('admin_servers_btn'))
    or F.text == F.text.in_(btn_text('admin_back_users_menu_btn'))
)
async def command(message: Message, state: FSMContext) -> None:
    lang = await get_lang(message.from_user.id, state)
    await message.answer(
        _('servers_control', lang),
        reply_markup=await server_menu(lang)
    )


@admin_router.message(F.text.in_(btn_text('admin_server_cancellation')))
async def back_server_menu_bot(message: Message, state: FSMContext) -> None:
    lang = await get_lang(message.from_user.id, state)
    await state.clear()
    await message.answer(
        _('servers_control', lang),
        reply_markup=await server_menu(lang)
    )


# todo:Вывод серверов
@admin_router.message(F.text.in_(btn_text('admin_server_show_all_btn')))
async def server_menu_bot(message: Message, state: FSMContext) -> None:
    lang = await get_lang(message.from_user.id, state)
    all_server = await get_all_server()
    if len(all_server) == 0:
        await message.answer(_('servers_none', lang))
        return
    await message.answer(_('list_all_servers', lang))
    space = 0
    for server in all_server:
        try:
            client_server = await get_static_client(server)
            space = len(client_server)
            if not await server_space_update(server.name, space):
                raise ("Failed to update the data about "
                       "the free space on the server")
            connect = True
        except Exception as e:
            log.error(e, 'error connecting to server')
            connect = False
        text_server = await get_server_info(server, space, connect, lang)
        await message.answer(
            **text_server.as_kwargs(),
            reply_markup=await server_control(server.work, server.name, lang),
        )


async def get_server_info(server, space, connect, lang):
    if connect:
        space_text = _('space_server_text', lang).format(
            space=space,
            max_space=CONFIG.max_people_server
        )
    else:
        space_text = _('server_not_connect_admin', lang)
    if server.work:
        work_text = _("server_use_s", lang)
    else:
        work_text = _("server_not_use_s", lang)
    if server.type_vpn == 0:
        return Text(
            _('server_name_s', lang), Code(server.name), '\n',
            _('server_adress_s', lang), Code(server.ip), '\n',
            _('server_password_vds_s', lang), Spoiler(server.vds_password),
            '\n', _('server_type_vpn_s', lang),
            ServerManager.VPN_TYPES.get(server.type_vpn).NAME_VPN, '\n',
            _('server_outline_connect_s', lang), Code(server.outline_link),
            '\n', work_text, '\n', space_text
        )
    else:
        return Text(
            _('server_name_s', lang), Code(server.name), '\n',
            _('server_adress_s', lang), Code(server.ip), '\n',
            _('server_password_vds_s', lang), Spoiler(server.vds_password),
            '\n', _('server_type_vpn_s', lang),
            ServerManager.VPN_TYPES.get(server.type_vpn).NAME_VPN, '\n',
            _('server_type_connect_s', lang),
            f'{"Https" if server.connection_method else "Http"}', '\n',
            _('server_panel_control_s', lang),
            f'{"Alireza 🕹" if server.panel == "alireza" else "Sanaei 🖲"}',
            '\n',
            _('server_id_connect_s', lang), Bold(server.inbound_id), '\n',
            _('server_login_s', lang), Bold(server.login), '\n',
            _('server_password_s', lang), Spoiler(server.password), '\n',
            work_text, '\n', space_text
        )


@admin_router.callback_query(ServerWork.filter())
async def callback_work_server(
        call: CallbackQuery,
        state: FSMContext,
        callback_data: ServerWork
):
    lang = await get_lang(call.from_user.id, state)
    text_working = _('server_use_active', lang).format(
        name_server=callback_data.name_server
    )
    text_uncorking = _('server_not_use_active', lang).format(
        name_server=callback_data.name_server
    )
    text_message = text_working if callback_data.work else text_uncorking
    await server_work_update(callback_data.name_server, callback_data.work)
    await call.message.answer(text_message)
    await call.answer()


async def get_static_client(server):
    server_manager = ServerManager(server)
    return await server_manager.get_all_user()


async def get_text_client(all_client, bot_client, lang):
    text_client = ''
    count = 1
    for client in bot_client:
        text_client += await string_user(client, count, lang)
        count += 1
        all_client.remove(str(client.tgid))
    for unknown_client in all_client:
        text_client += _('not_found_key', lang).format(
            unknown_client=unknown_client
        )
    return text_client


@admin_router.callback_query(ServerUserList.filter())
async def call_list_server(
        call: CallbackQuery,
        callback_data: ServerUserList,
        state: FSMContext
):
    lang = await get_lang(call.from_user.id, state)
    server = await get_server(callback_data.name_server)
    try:
        client_stats = await get_static_client(server)
    except Exception as e:
        await call.message.answer(_('server_not_connect_admin', lang))
        await call.answer()
        log.error(e, 'server not connect')
        return
    try:
        if server.type_vpn == 0:
            client_id = list({client.name for client in client_stats})
        else:
            client_id = list({client['email'] for client in client_stats})
        bot_client = await get_person_id(client_id)
        if not callback_data.action:
            await delete_users_server(call.message, server, bot_client, lang)
            await call.message.answer(
                _('key_delete_server', lang)
                .format(name=callback_data.name_server)
            )
            await call.answer()
            return
        text_client = await get_text_client(client_id, bot_client, lang)
    except Exception as e:
        await call.message.answer(_('error_get_users_bd_text', lang))
        await call.answer()
        log.error(e, 'error get users BD')
        return
    if text_client == '':
        await call.message.answer(_('file_server_user_none', lang))
        await call.answer()
        return
    file_stream = io.BytesIO(text_client.encode()).getvalue()
    input_file = BufferedInputFile(file_stream, 'Clients_server.txt')
    try:
        await call.message.answer_document(
            input_file,
            caption=_('file_list_users_server', lang)
            .format(name_server=callback_data.name_server)
        )
    except Exception as e:
        await call.message.answer(_('error_file_list_users_server', lang))
        log.error(e, 'error file send Clients_server.txt')
    await call.answer()


async def delete_users_server(m, server, users, lang):
    server_manager = ServerManager(server)
    for user in users:
        try:
            await server_manager.delete_client(user.tgid)
        except Exception as e:
            log.error(e, 'not delete users server')
            await m.answer(_('error_delete_all_users_server', lang))
            return False
    await update_delete_users_server(server)
    return True


@admin_router.message(
    StateFilter(None),
    F.text.in_(btn_text('admin_server_add_btn'))
)
async def add_server_bot(message: Message, state: FSMContext) -> None:
    lang = await get_lang(message.from_user.id, state)
    await message.answer(
        _('input_name_server_admin', lang),
        reply_markup=await back_server_menu(lang))
    await state.set_state(AddServer.input_name)


@admin_router.message(F.text.in_(btn_text('admin_server_delete_btn')))
async def delete_server_bot(message: Message, state: FSMContext) -> None:
    lang = await get_lang(message.from_user.id, state)
    await message.answer(
        _('input_name_server_admin', lang),
        reply_markup=await back_server_menu(lang)
    )
    await state.set_state(RemoveServer.input_name)


# todo: Mailing list management
@admin_router.message(F.text.in_(btn_text('admin_send_message_users_btn')))
async def out_message_bot(message: Message, state: FSMContext) -> None:
    lang = await get_lang(message.from_user.id, state)
    await message.answer(
        _('who_should_i_send', lang),
        reply_markup=await missing_user_menu(lang)
    )


@admin_router.callback_query(MissingMessage.filter())
async def update_message_bot(
        call: CallbackQuery,
        callback_data: MissingMessage,
        state: FSMContext) -> None:
    lang = await get_lang(call.from_user.id, state)
    if callback_data.option == 'update':
        try:
            users = await get_all_user()
            await update_client(call.message, users, lang)
        except Exception as e:
            await call.message.answer(_('error_update', lang))
            log.error(e, 'not update menu all users')
        await call.answer()
        return
    await state.update_data(option=callback_data.option)
    await call.message.answer(
        _('input_message_or_image', lang),
        reply_markup=await back_admin_menu(lang)
    )
    await call.answer()
    await state.set_state(StateMailing.input_text)


@state_admin_router.message(StateMailing.input_text)
async def mailing_text(message: Message, state: FSMContext):
    lang = await get_lang(message.from_user.id, state)
    try:
        data = await state.get_data()
        if data['option'] == 'all':
            users = await get_all_user()
        elif data['option'] == 'sub':
            users = await get_all_subscription()
        else:
            users = await get_no_subscription()
        count_not_suc = 0
        if message.photo:
            photo = message.photo[-1]
            caption = message.caption if message.caption else ''
            for user in users:
                try:
                    await message.bot.send_photo(
                        user.tgid,
                        photo.file_id,
                        caption=caption
                    )
                except Exception as e:
                    log.info(e, 'user block bot')
                    count_not_suc += 1
                    continue
        else:
            for user in users:
                try:
                    await message.bot.send_message(
                        user.tgid, message.text
                    )
                except Exception as e:
                    log.info(e, 'user block bot')
                    count_not_suc += 1
                    continue
        await message.answer(
            _('result_mailing_text', lang).format(
                all_count=len(users),
                suc_count=len(users) - count_not_suc,
                count_not_suc=count_not_suc
            ),
            reply_markup=await admin_menu(lang)
        )
    except Exception as e:
        log.error(e, 'error mailing')
        await message.answer(_('error_mailing_text', lang))
    await state.clear()


async def update_client(message, users, lang):
    for user in users:
        try:
            await message.bot.send_message(
                user.tgid, _('main_message', user.lang),
                reply_markup=await user_menu(user, user.lang)
            )
        except Exception as e:
            log.info(e, 'user block bot')
            continue
    await message.answer(
        _('bot_update_success', lang)
    )
