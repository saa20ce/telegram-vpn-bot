import logging

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram.utils.deep_linking import create_start_link
from aiogram.utils.formatting import Text, Italic
from sqlalchemy.exc import InvalidRequestError

from bot.database.methods.get import (
    get_promo_code,
    get_person,
    get_count_referral_user, get_referral_balance
)
from bot.database.methods.insert import add_withdrawal
from bot.database.methods.update import (
    add_pomo_code_person,
    reduce_referral_balance_person
)
from bot.keyboards.inline.user_inline import (
    share_link,
    promo_code_button,
    message_admin_user
)
from bot.keyboards.reply.user_reply import back_menu, user_menu
from bot.misc.language import Localization, get_lang
from bot.misc.util import CONFIG

log = logging.getLogger(__name__)

referral_router = Router()

_ = Localization.text
btn_text = Localization.get_reply_button


class ActivatePromocode(StatesGroup):
    input_promo = State()


class WithdrawalFunds(StatesGroup):
    input_amount = State()
    payment_method = State()
    communication = State()
    input_message_admin = State()


async def get_referral_link(message):
    return await create_start_link(
        message.bot,
        str(message.from_user.id),
        encode=True
    )


@referral_router.message(F.text.in_(btn_text('bonus_btn')))
async def give_handler(m: Message, state: FSMContext) -> None:
    lang = await get_lang(m.from_user.id, state)
    link_ref = await get_referral_link(m)
    message_text = Text(
        _('your_referral_link', lang).format(link_ref=link_ref),
        _('referral_message', lang)
    )
    await m.answer(
        **message_text.as_kwargs(),
        reply_markup=await share_link(link_ref, lang)
    )
    await m.answer(
        _('referral_promo_code', lang),
        reply_markup=await promo_code_button(lang)
    )


@referral_router.message(F.text.in_(btn_text('affiliate_btn')))
async def referral_system_handler(m: Message, state: FSMContext) -> None:
    lang = await get_lang(m.from_user.id, state)
    count_referral_user = await get_count_referral_user(m.from_user.id)
    balance = await get_referral_balance(m.from_user.id)
    link_ref = await get_referral_link(m)
    message_text = (
        _('your_referral_link', lang).format(link_ref=link_ref) +
        _('referral_system_message', lang) + '\n' +
        _('affiliate_reff_text', lang)
        .format(
            referral_percent=CONFIG.referral_percent,
            minimum_amount=CONFIG.minimum_withdrawal_amount,
            count_referral_user=count_referral_user,
            balance=balance
        )
    )
    await m.answer(
        message_text,
        reply_markup=await share_link(link_ref, lang, balance)
    )


@referral_router.callback_query(F.data == 'promo_code')
async def successful_payment(call: CallbackQuery, state: FSMContext):
    lang = await get_lang(call.from_user.id, state)
    await call.message.answer(
        _('input_promo_user', lang),
        reply_markup=await back_menu(lang)
    )
    await call.answer()
    await state.set_state(ActivatePromocode.input_promo)


@referral_router.callback_query(F.data == 'withdrawal_of_funds')
async def withdrawal_of_funds(call: CallbackQuery, state: FSMContext):
    lang = await get_lang(call.from_user.id, state)
    await call.message.answer(
        _('input_amount_withdrawal_min', lang)
        .format(minimum_amount=CONFIG.minimum_withdrawal_amount),
        reply_markup=await back_menu(lang)
    )
    await call.answer()
    await state.set_state(WithdrawalFunds.input_amount)


@referral_router.message(WithdrawalFunds.input_amount)
async def payment_method(message: Message, state: FSMContext):
    lang = await get_lang(message.from_user.id, state)
    amount = message.text.strip()
    try:
        amount = int(amount)
    except Exception as e:
        log.info(e, 'incorrect amount')
    balance = await get_referral_balance(message.from_user.id)
    if (
            type(amount) is not int or
            CONFIG.minimum_withdrawal_amount > amount or
            amount > balance
    ):
        await message.answer(_('error_incorrect', lang))
        return
    await state.update_data(amount=amount)
    await message.answer(_('where_transfer_funds', lang))
    await state.set_state(WithdrawalFunds.payment_method)


@referral_router.message(WithdrawalFunds.payment_method)
async def choosing_connect(message: Message, state: FSMContext):
    lang = await get_lang(message.from_user.id, state)
    await state.update_data(payment_info=message.text.strip())
    await message.answer(_('how_i_contact_you', lang))
    await state.set_state(WithdrawalFunds.communication)


@referral_router.message(WithdrawalFunds.communication)
async def save_payment_method(message: Message, state: FSMContext):
    lang = await get_lang(message.from_user.id, state)
    communication = message.text.strip()
    data = await state.get_data()
    payment_info = data['payment_info']
    amount = data['amount']
    person = await get_person(message.from_user.id)
    try:
        await add_withdrawal(
            amount=amount,
            payment_info=payment_info,
            tgid=message.from_user.id,
            communication=communication
        )
    except Exception as e:
        log.error(e, 'error add withdrawal')
        await message.answer(_('error_send_admin', lang))
        await state.clear()
    if await reduce_referral_balance_person(amount, message.from_user.id):
        await message.answer(
            _('referral_system_success', lang),
            reply_markup=await user_menu(person, lang)
        )
        await message.bot.send_message(
            CONFIG.admin_tg_id,
            _(
                'withdrawal_funds_has_been',
                await get_lang(message.from_user.id)
            ).format(amount=amount)
        )
    else:
        await message.answer(
            _('error_withdrawal_funds_not_balance', lang),
            reply_markup=await user_menu(person, lang)
        )
    await state.clear()


@referral_router.message(ActivatePromocode.input_promo)
async def promo_check(message: Message, state: FSMContext):
    lang = await get_lang(message.from_user.id, state)
    text_promo = message.text.strip()
    person = await get_person(message.from_user.id)
    promo_code = await get_promo_code(text_promo)
    if promo_code is not None:
        try:
            add_balance_text = promo_code.add_balance
            await add_pomo_code_person(
                message.from_user.id,
                promo_code
            )
            await message.answer(
                _('promo_success_user', lang).format(amount=add_balance_text),
                reply_markup=await user_menu(person, lang)
            )
        except InvalidRequestError:
            await message.answer(
                _('uses_promo_user', lang),
                reply_markup=await user_menu(person, lang)
            )
    else:
        await message.answer(
            _('referral_promo_code_none', lang),
            reply_markup=await user_menu(person, lang)
        )
    await state.clear()


@referral_router.callback_query(F.data == 'message_admin')
async def message_admin(callback_query: CallbackQuery, state: FSMContext):
    lang = await get_lang(callback_query.from_user.id, state)
    await callback_query.message.answer(
        _('input_message_user_admin', lang),
        reply_markup=await back_menu(lang)
    )
    await state.set_state(WithdrawalFunds.input_message_admin)
    await callback_query.answer()


@referral_router.message(WithdrawalFunds.input_message_admin)
async def input_message_admin(message: Message, state: FSMContext):
    lang = await get_lang(message.from_user.id, state)
    person = await get_person(message.from_user.id)
    try:
        text = Text(
            _('message_user_admin', lang)
            .format(
                fullname=person.fullname,
                username=person.username,
                telegram_id=person.tgid
            ),
            Italic(message.text.strip())
        )
        await message.bot.send_message(
            CONFIG.admin_tg_id, **text.as_kwargs(),
            reply_markup=await message_admin_user(person.tgid, lang)
        )
        await message.answer(
            _('message_user_admin_success', lang),
            reply_markup=await user_menu(person, lang)
        )
    except Exception as e:
        await message.answer(
            _('error_message_user_admin_success', lang),
            reply_markup=await user_menu(person, lang)
        )
        log.error(e, 'Error admin message')
    await state.clear()
