import io
import logging
from datetime import datetime

from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import (
    Message,
    CallbackQuery,
    BufferedInputFile
)
from aiogram.utils.formatting import Text, Code, Bold

from bot.database.methods.delete import delete_static_user_bd
from bot.database.methods.get import (
    get_all_user,
    get_all_subscription,
    get_payments,
    get_person, get_server, get_all_static_user
)
from bot.database.methods.insert import add_static_user
from bot.database.methods.update import (
    add_time_person,
    person_banned_true,
    update_balance_person
)
from bot.keyboards.reply.admin_reply import (
    admin_user_menu,
    back_user_menu,
    show_user_menu,
    static_user_menu,
    back_static_user_menu
)
from bot.keyboards.inline.admin_inline import (
    edit_client_menu,
    delete_time_client,
    delete_static_user
)
from bot.keyboards.reply.user_reply import user_menu, back_menu, balance_menu
from bot.misc.VPN.ServerManager import ServerManager
from bot.misc.callbackData import (
    EditUserPanel,
    DeleteTimeClient,
    DeleteStaticUser,
    MessageAdminUser, EditBalanceUser
)
from bot.misc.language import Localization, get_lang
from bot.misc.loop import delete_key
from bot.misc.util import CONFIG

log = logging.getLogger(__name__)

_ = Localization.text
btn_text = Localization.get_reply_button

FORMAT_DATA = "%d.%m.%Y %H:%M"
ONE_HOUSE = 3600
DEFAULT_UTC = CONFIG.UTC_time * ONE_HOUSE

user_management_router = Router()


class EditUser(StatesGroup):
    show_user = State()
    add_time = State()
    delete_time = State()
    input_message_user = State()
    input_balance_user = State()


class StaticUser(StatesGroup):
    static_user_server = State()
    static_user_name = State()


# todo: User management
@user_management_router.message(
    (F.text.in_(btn_text('admin_users_btn')))
    | (F.text.in_(btn_text('admin_back_users_menu_btn')))
)
async def command(message: Message, state: FSMContext) -> None:
    lang = await get_lang(message.from_user.id, state)
    await message.answer(
        _('method_replenishment', lang),
        reply_markup=await admin_user_menu(lang)
    )


@user_management_router.message(
    F.text.in_(btn_text('admin_show_statistic_btn'))
)
async def control_user_handler(message: Message, state: FSMContext) -> None:
    lang = await get_lang(message.from_user.id, state)
    await message.answer(
        _('method_replenishment', lang),
        reply_markup=await show_user_menu(lang)
    )


@user_management_router.message(
    F.text.in_(btn_text('admin_statistic_show_all_users_btn'))
)
async def show_user_handler(message: Message, state: FSMContext) -> None:
    lang = await get_lang(message.from_user.id, state)
    all_users = await get_all_user()
    str_user = ''
    count = 1
    for user in all_users:
        str_user += await string_user(user, count, lang)
        count += 1
    file_stream = io.BytesIO(str_user.encode()).getvalue()
    input_file = BufferedInputFile(file_stream, 'all_user.txt')
    try:
        await message.answer_document(
            input_file,
            caption=_('list_of_all_users_file', lang)
        )
    except Exception as e:
        await message.answer(_('error_list_of_all_users_file', lang))
        log.error(e, 'error send file all_user.txt')


@user_management_router.message(
    F.text.in_(btn_text('admin_statistic_show_sub_users_btn'))
)
async def show_user_sub_handler(message: Message, state: FSMContext) -> None:
    lang = await get_lang(message.from_user.id, state)
    sub_users = await get_all_subscription()
    str_sub_user = ''
    count = 1
    for user in sub_users:
        str_sub_user += await string_user(user, count, lang)
        count += 1
    if str_sub_user == '':
        await message.answer(_('none_list_of_sub_users_file', lang))
        return
    file_stream = io.BytesIO(str_sub_user.encode()).getvalue()
    input_file = BufferedInputFile(file_stream, 'subscription_user.txt')
    try:
        await message.answer_document(
            input_file,
            caption=_('list_of_sub_users_file', lang)
        )
    except Exception as e:
        await message.answer(_('error_list_of_sub_users_file', lang))
        log.error(e, 'error send file subscription_user.txt')


@user_management_router.message(
    F.text.in_(btn_text('admin_statistic_show_payments_btn'))
)
async def back_server_menu_bot(message: Message, state: FSMContext) -> None:
    lang = await get_lang(message.from_user.id, state)
    payments = await get_payments()
    str_payments = ''
    count = 1
    for payment in payments:
        str_payments += (
            _('write_payments_file_str', lang)
            .format(
                count=count,
                user=payment.user,
                payment_system=payment.payment_system,
                amount=payment.amount,
                date=payment.data
            )
        )
        count += 1
    if str_payments == '':
        await message.answer(_('none_list_of_payments_file', lang))
        return
    file_stream = io.BytesIO(str_payments.encode()).getvalue()
    input_file = BufferedInputFile(file_stream, 'payments.txt')
    try:
        await message.answer_document(
            input_file,
            caption=_('list_of_payments_file', lang)
        )
    except Exception as e:
        await message.answer(_('error_list_of_payments_file', lang))
        log.error(e, 'error send file payments.txt')


@user_management_router.message(
    F.text.in_(btn_text('admin_edit_user_btn'))
)
async def edit_user_handler(message: Message, state: FSMContext) -> None:
    lang = await get_lang(message.from_user.id, state)
    await message.answer(
        _('input_telegram_id_user_m', lang),
        reply_markup=await back_user_menu(lang)
    )
    await state.set_state(EditUser.show_user)


@user_management_router.message(
    (F.text.in_(btn_text('admin_users_cancellation')))
    | (F.text.in_(btn_text('admin_exit_btn')))
)
async def back_user_control(message: Message, state: FSMContext) -> None:
    lang = await get_lang(message.from_user.id, state)
    await state.clear()
    await message.answer(
        _('admin_user_manager_m', lang),
        reply_markup=await admin_user_menu(lang)
    )


@user_management_router.message(EditUser.show_user)
async def show_user_state(message: Message, state: FSMContext) -> None:
    lang = await get_lang(message.from_user.id, state)
    try:
        client = await get_person(int(message.text.strip()))
        subscription = await time_sub_client(client)
        if subscription:
            sub_text = _('card_client_admin_m_sub', lang).format(
                subscription=subscription
            )
        else:
            sub_text = _('card_client_admin_m_none_sub', lang)
        content = Text(
            _('card_client_admin_m', lang).format(
                fullname=client.fullname,
                username=client.username,
                telegram_id=client.tgid,
                balance=client.balance,
                referral_balance=client.referral_balance
            ),
            sub_text
        )
        await message.answer(
            **content.as_kwargs(),
            reply_markup=await edit_client_menu(client.tgid, lang)
        )
        await state.update_data(client=client)

    except Exception as e:
        log.info(e, 'client not found')
        await message.answer(
            _('card_client_admin_m_client_none', lang),
            reply_markup=await admin_user_menu(lang)
        )
        await state.clear()


@user_management_router.callback_query(EditUserPanel.filter())
async def callback_work_server(
        call: CallbackQuery,
        callback_data: EditUserPanel,
        state: FSMContext):
    lang = await get_lang(call.from_user.id, state)
    if callback_data.action == 'add_time':
        await call.message.answer(_('input_count_day_add_time_m', lang))
        await state.set_state(EditUser.add_time)
    else:
        await call.message.edit_reply_markup(
            call.message.forward_from_message_id,
            reply_markup=await delete_time_client(lang)
        )
    await call.answer()


@user_management_router.callback_query(EditBalanceUser.filter())
async def edit_balance_call(
        call: CallbackQuery,
        callback_data: EditBalanceUser,
        state: FSMContext):
    lang = await get_lang(call.from_user.id, state)
    await call.message.answer(
        _('input_balance_add_user_m', lang),
        reply_markup=await back_user_menu(lang)
    )
    await state.update_data(id_user=callback_data.id_user)
    await state.set_state(EditUser.input_balance_user)
    await call.answer()


@user_management_router.message(EditUser.input_balance_user)
async def edit_balance_state(message: Message, state: FSMContext) -> None:
    lang = await get_lang(message.from_user.id, state)
    try:
        amount = int(message.text.strip())
        if 0 > amount or amount > 1000000:
            await message.answer(_('input_balance_limit_m', lang))
            return
    except Exception as e:
        log.info(e, 'incorrect input edit balance')
        await message.answer(_('incorrect_input_edit_balance', lang))
        return
    data = await state.get_data()
    await state.clear()
    if await update_balance_person(amount, data['id_user']):
        person = await get_person(data['id_user'])
        await message.answer(
            _('input_balance_success_m', lang),
            reply_markup=await admin_user_menu(lang)
        )
        try:
            lang_user = await get_lang(data['id_user'])
            await message.bot.send_message(
                data['id_user'],
                _('user_message_input_balance_admin_m', lang_user)
                .format(balance=person.balance),
                reply_markup=await balance_menu(person, lang_user)
            )
        except Exception as e:
            log.info(e, 'user blocked bot')
            await message.answer(_('message_user_block_bot', lang))
    else:
        await message.answer(_('error_write_bd_new_balance', lang))


@user_management_router.message(EditUser.add_time)
async def add_time_user_state(message: Message, state: FSMContext) -> None:
    lang = await get_lang(message.from_user.id, state)
    try:
        if message.text.strip() in btn_text('admin_users_cancellation'):
            await state.clear()
            await message.answer(
                _('back_you_back', lang),
                reply_markup=await admin_user_menu(lang)
            )
            return
        count_day = int(message.text.strip())
        if count_day > 2000:
            await message.answer(_('limit_count_day_sub_m', lang))
            return
    except Exception as e:
        log.info(e, 'incorrect input count day sub')
        await message.answer(_('incorrect_input_count_day_sub', lang))
        return
    try:
        user_data = await state.get_data()
        client = user_data['client']
        await add_time_person(client.tgid, count_day * (ONE_HOUSE * 24))
        await state.clear()
        await message.answer(
            _('incorrect_input_count_day_sub', lang).format(
                username=client.username
            ),
            reply_markup=await admin_user_menu(lang)
        )
    except Exception as e:
        log.error(e, 'error add time user')
        await message.answer(_('error_not_found', lang))
        await state.clear()
        return
    try:
        client = await get_person(client.tgid)
        await message.bot.send_message(
            client.tgid,
            _('donated_days', client.lang),
            reply_markup=await user_menu(client, client.lang),
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        log.info(e, 'user block bot')
        await message.answer(_('error_input_count_day_sub_success', lang))
        return


@user_management_router.callback_query(DeleteTimeClient.filter())
async def delete_time_user_callback(call: CallbackQuery, state: FSMContext):
    lang = await get_lang(call.from_user.id, state)
    try:
        user_data = await state.get_data()
        client = user_data['client']
        await person_banned_true(client.tgid)
        if client.server is not None:
            await delete_key(client)
        await call.message.answer(
            _('user_delete_time_m', lang).format(username=client.username),
            reply_markup=await admin_user_menu(lang)
        )
        await call.answer()
        await state.clear()
    except Exception as e:
        log.error(e, 'error delete key or person banned')
        await call.message.answer(_('error_not_found', lang))
        await state.clear()
        return
    try:
        client = await get_person(client.tgid)
        await call.message.bot.send_message(
            client.tgid,
            _('ended_sub_message', client.lang),
            reply_markup=await user_menu(client, client.lang)
        )
    except Exception as e:
        await call.message.answer(_('error_user_delete_time_m', lang))
        log.info(e, 'user block bot')


@user_management_router.message(F.text.in_(btn_text('admin_static_user_btn')))
async def static_user_menu_handler(
        message: Message,
        state: FSMContext
) -> None:
    lang = await get_lang(message.from_user.id, state)
    await message.answer(
        _('select_menu_item', lang),
        reply_markup=await static_user_menu(lang)
    )


@user_management_router.message(
    F.text.in_(btn_text('admin_static_add_user_btn'))
)
async def add_static_user_handler(message: Message, state: FSMContext) -> None:
    lang = await get_lang(message.from_user.id, state)
    await message.answer(
        _('input_server_name', lang),
        reply_markup=await back_static_user_menu(lang)
    )
    await state.set_state(StaticUser.static_user_server)


@user_management_router.message(StaticUser.static_user_server)
async def input_username_static(message: Message, state: FSMContext) -> None:
    lang = await get_lang(message.from_user.id, state)
    server = await get_server(message.text.strip())
    if server is not None:
        await state.update_data(server=server)
        await message.answer(_('static_input_name_user', lang))
        await state.set_state(StaticUser.static_user_name)
    else:
        await message.answer(_('server_not_found', lang))


@user_management_router.message(StaticUser.static_user_name)
async def add_user_in_server(message: Message, state: FSMContext) -> None:
    lang = await get_lang(message.from_user.id, state)
    if len(message.text.encode()) > 15:
        await message.answer(_('incorrect_name_user', lang))
        return
    user_data = await state.get_data()
    server = user_data['server']
    name = message.text.strip()
    try:
        sever_manager = ServerManager(server)
        await sever_manager.add_client(name)
    except Exception as e:
        log.error(e, 'error connecting to server')
        await message.answer(_('error_connect_serer', lang))
        return
    try:
        await add_static_user(name, server.id)
    except Exception as e:
        log.error(e, 'error add static user')
        await message.answer(_('error_write_bd_key_create', lang))
    await message.answer(
        _('static_user_create_success', lang).format(
            name=name,
            server_name=server.name
        ),
        reply_markup=await static_user_menu(lang)
    )
    await state.clear()


@user_management_router.message(
    F.text.in_(btn_text('admin_static_show_users_btn'))
)
async def show_static_user_handler(
        message: Message,
        state: FSMContext
) -> None:
    lang = await get_lang(message.from_user.id, state)
    try:
        all_static_user = await get_all_static_user()
        if len(all_static_user) == 0:
            await message.answer(_('none_list_static_user', lang))
            return
    except Exception as e:
        log.error(e, 'error get all static user')
        await message.answer(_('error_get_static_user', lang))
        return
    await message.answer(_('list_static_user', lang))
    for static_user in all_static_user:
        try:
            if static_user.server is not None:
                config = await get_config_client(
                    static_user.server_table,
                    static_user.name
                )
            else:
                await delete_static_user_bd(static_user.name)
                await message.answer(
                    _('list_static_user_none_server_delete', lang)
                )
                continue
            message_text = Text(
                _('show_user', lang), Bold(static_user.name), '\n',
                _('show_key', lang), Code(config)
            )
            await message.answer(
                **message_text.as_kwargs(),
                reply_markup=await delete_static_user(
                    static_user.name,
                    static_user.server_table.name,
                    lang
                )
            )
        except Exception as e:
            log.error(e, 'error connect server')
            await message.answer(
                _('error_connect_server', lang).format(
                    name_server=static_user.server_table.name
                )
            )
            continue


@user_management_router.callback_query(DeleteStaticUser.filter())
async def delete_static_user_callback(
        call: CallbackQuery,
        state: FSMContext,
        callback_data: DeleteStaticUser):
    lang = await get_lang(call.from_user.id, state)
    try:
        server = await get_server(callback_data.server_name)
        server_manager = ServerManager(server)
        if not await server_manager.delete_client(callback_data.name):
            raise Exception("Couldn't delete it")
    except Exception as e:
        await call.message.answer(
            _('error_delete_static_user_in_server', lang).format(
                name=callback_data.name
            )
        )
        log.error(e, 'error delete static user')
        return
    try:
        await delete_static_user_bd(callback_data.name)
    except Exception as e:
        await call.message.answer(_('error_delete_bd_static_user', lang))
        log.error(e, 'error delete BD static user')
        return
    await call.message.answer(
        _('delete_static_user_success', lang)
        .format(name=callback_data.name)
    )
    await call.answer()


async def string_user(client, count, lang):
    subscription = await time_sub_client(client)
    return _('show_client_file_str', lang).format(
        count=count,
        fullname=client.fullname,
        username=client.username,
        telegram_id=client.tgid,
        balance=client.balance,
        referral_balance=client.referral_balance,
        subscription=subscription
    )


async def time_sub_client(client):
    client_data = int(client.subscription) + DEFAULT_UTC
    data = f'{datetime.utcfromtimestamp(client_data).strftime(FORMAT_DATA)}'
    data_string = f' - {data}'
    return f'{"" if client.banned is True else data_string}'


async def get_config_client(server, name):
    serve_manager = ServerManager(server)
    return await serve_manager.get_key(name=name, name_key=CONFIG.name)


@user_management_router.callback_query(MessageAdminUser.filter())
async def message_admin_callback_query(
        call: CallbackQuery,
        state: FSMContext,
        callback_data: MessageAdminUser):
    lang = await get_lang(call.from_user.id, state)
    await call.message.delete()
    await call.message.answer(
        _('input_message_admin_user', lang),
        reply_markup=await back_menu(lang))
    await state.update_data(tgid=callback_data.id_user)
    await state.set_state(EditUser.input_message_user)
    await call.answer()


@user_management_router.message(EditUser.input_message_user)
async def edit_user_callback_query(message: Message, state: FSMContext):
    lang = await get_lang(message.from_user.id, state)
    text = Text(
        Bold(_('message_from_the_admin', lang)), '\n',
        message.text.strip()
    )
    data = await state.get_data()
    try:
        await message.bot.send_message(int(data['tgid']), **text.as_kwargs())
        await message.answer(
            _('message_from_success', lang),
            reply_markup=await admin_user_menu(lang)
        )
    except Exception as e:
        log.info(e, 'Error send message admin -- user')
        await message.answer(
            _('message_user_block_bot', lang),
            reply_markup=await admin_user_menu(lang)
        )
    await state.clear()
