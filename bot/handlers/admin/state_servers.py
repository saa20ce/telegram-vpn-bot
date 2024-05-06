import logging

from aiogram import Router
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from bot.database.methods.insert import add_server
from bot.database.methods.delete import delete_server
from bot.database.models.main import Servers
from bot.keyboards.inline.admin_inline import (
    choosing_connection,
    choosing_panel, choosing_vpn
)
from bot.keyboards.reply.admin_reply import server_menu
from bot.misc.VPN.ServerManager import ServerManager
from bot.misc.callbackData import (
    ChoosingConnectionMethod,
    ChoosingPanel,
    ChoosingVPN
)
from bot.misc.language import Localization, get_lang

log = logging.getLogger(__name__)

_ = Localization.text
btn_text = Localization.get_reply_button

state_admin_router = Router()


class RemoveServer(StatesGroup):
    input_name = State()


class AddServer(StatesGroup):
    input_name = State()
    input_ip = State()
    input_password_vds = State()
    input_type_vpn = State()
    input_connect = State()
    input_panel = State()
    input_login = State()
    input_password = State()
    input_inbound_id = State()
    input_url_cert = State()


@state_admin_router.message(AddServer.input_name)
async def input_name(message: Message, state: FSMContext):
    lang = await get_lang(message.from_user.id, state)
    if len(message.text.encode()) > 30:
        await message.answer(_('server_name_error', lang))
        return
    await state.update_data(name=message.text.strip())
    await message.answer(_('server_input_ip_text', lang))
    await state.set_state(AddServer.input_ip)


@state_admin_router.message(AddServer.input_ip)
async def input_ip(message: Message, state: FSMContext):
    lang = await get_lang(message.from_user.id, state)
    await state.update_data(ip=message.text.strip())
    await message.answer(_('server_input_password_text', lang))
    await state.set_state(AddServer.input_password_vds)


@state_admin_router.message(AddServer.input_password_vds)
async def input_password_vds(message: Message, state: FSMContext):
    lang = await get_lang(message.from_user.id, state)
    await state.update_data(vds_password=message.text.strip())
    await message.answer(
        _('server_input_type_vpn_text', lang),
        reply_markup=await choosing_vpn()
    )
    await state.set_state(AddServer.input_type_vpn)


@state_admin_router.callback_query(
    ChoosingVPN.filter(),
    AddServer.input_type_vpn
)
async def input_type_connect(
        call: CallbackQuery,
        state: FSMContext,
        callback_data: ChoosingVPN):
    lang = await get_lang(call.from_user.id, state)
    await state.update_data(type_vpn=callback_data.type)
    if callback_data.type == 0:
        await call.message.answer(
            _('server_input_url_cert_text', lang),
        )
        await state.set_state(AddServer.input_url_cert)
    elif callback_data.type == 1 or callback_data.type == 2:
        await call.message.answer(
            _('server_input_choosing_type_connect_text', lang),
            reply_markup=await choosing_connection()
        )
        await state.set_state(AddServer.input_connect)
    else:
        await call.message.answer(
            _('server_error_choosing_type_connect_text', lang),
            reply_markup=await server_menu(lang)
        )
        await state.clear()
    await call.answer()


@state_admin_router.message(AddServer.input_url_cert)
async def input_url_cert(message: Message, state: FSMContext):
    await state.update_data(outline_link=message.text.strip())
    user_data = await state.get_data()
    await create_new_server(message, state, user_data)
    await state.clear()


@state_admin_router.callback_query(
    ChoosingConnectionMethod.filter(),
    AddServer.input_connect
)
async def callback_connect(
        call: CallbackQuery,
        callback_data: ChoosingConnectionMethod,
        state: FSMContext
):
    lang = await get_lang(call.from_user.id, state)
    await state.update_data(connection_method=callback_data.connection)
    await call.message.answer(
        _('server_choosing_panel_control', lang),
        reply_markup=await choosing_panel()
    )
    await call.answer()
    await state.set_state(AddServer.input_panel)


@state_admin_router.callback_query(
    ChoosingPanel.filter(),
    AddServer.input_panel
)
async def input_id_connect(
        call: CallbackQuery,
        callback_data: ChoosingConnectionMethod,
        state: FSMContext
):
    await state.update_data(panel=callback_data.panel)
    await call.message.answer(_(
        'server_input_id_connect_text',
        await get_lang(call.from_user.id, state)
    ))
    await call.answer()
    await state.set_state(AddServer.input_inbound_id)


@state_admin_router.message(AddServer.input_inbound_id)
async def input_inbound_id_handler(message: Message, state: FSMContext):
    await state.update_data(inbound_id=message.text.strip())
    await message.answer(_(
        'server_input_login_text',
        await get_lang(message.from_user.id, state))
    )
    await state.set_state(AddServer.input_login)


@state_admin_router.message(AddServer.input_login)
async def input_login(message: Message, state: FSMContext):
    await state.update_data(login=message.text.strip())
    await message.answer(_(
        'server_input_password_panel_text',
        await get_lang(message.from_user.id, state)
    )
    )
    await state.set_state(AddServer.input_password)


@state_admin_router.message(AddServer.input_password)
async def input_password(message: Message, state: FSMContext):
    await state.update_data(password=message.text.strip())
    user_data = await state.get_data()
    await create_new_server(message, state, user_data)
    await state.clear()


async def create_new_server(message, state, user_data):
    lang = await get_lang(message.from_user.id, state)
    del user_data['lang']
    try:
        server = Servers.create_server(user_data)
        server_manager = ServerManager(server)
        connect = await server_manager.get_all_user()
        if connect is None:
            raise ModuleNotFoundError
    except Exception as e:
        await message.answer(
            _('server_error_connect', lang),
            reply_markup=await server_menu(lang)
        )
        await state.clear()
        log.error(e, 'state_server.py not connect server')
        return
    try:
        await add_server(server)
    except Exception as e:
        await message.answer(
            _('server_error_write_db_name', lang),
            reply_markup=await server_menu(lang)
        )
        await state.clear()
        log.error(e, 'state_server.py not read server database')
        return
    await message.answer(
        _('server_add_success', lang),
        reply_markup=await server_menu(lang)
    )


@state_admin_router.message(RemoveServer.input_name)
async def delete_server_handler(message: Message, state: FSMContext):
    lang = await get_lang(message.from_user.id, state)
    name_server = message.text.strip()
    try:
        await delete_server(name_server)
    except ModuleNotFoundError:
        await message.answer(
            _('server_error_name_not_found', lang),
            reply_markup=await server_menu(lang)
        )
        await state.clear()
        return
    except Exception as e:
        await message.answer(
            _('server_error_delete', lang),
            reply_markup=await server_menu(lang)
        )
        await state.clear()
        log.error(e, 'error delete server')
        return
    await message.answer(
        _('server_delete_success', lang),
        reply_markup=await server_menu(lang)
    )
    await state.clear()
