import logging

from bot.database.methods.get import get_person
from bot.database.methods.insert import add_payment
from bot.database.methods.update import (
    add_balance_person,
    add_referral_balance_person,
    add_time_person,
    update_person_trial_status
)

from bot.keyboards.reply.user_reply import balance_menu
from bot.misc.language import Localization, get_lang
from bot.misc.loop import check_auto_renewal
from bot.misc.util import CONFIG

log = logging.getLogger(__name__)

_ = Localization.text


class PaymentSystem:
    TOKEN: str
    TEN_MINUTE = 60*30
    STEP = 5

    def __init__(self, message, user_id, price=None):
        self.message = message
        self.user_id = user_id
        self.price = price

    async def to_pay(self):
        raise NotImplementedError()

    async def successful_payment(self, total_amount, name_payment, payment_method_id=None, is_trial=False):
        log.info(
            f'user ID: {self.user_id}'
            f' success payment {total_amount} RUB'
        )
        lang_user = await get_lang(self.user_id)
        person = await get_person(self.user_id)
        if not person:
            await self.message.answer(_('error_person_not_found', lang_user))
            return
        log.debug(f"Adding balance: User ID={person.id}, Old Balance={person.balance}, Deposit={total_amount}")
        if is_trial:
            trial_duration_seconds = CONFIG.trial_duration_days * CONFIG.COUNT_SECOND_DAY
            await update_person_trial_status(self.user_id, True)
            await self.message.answer(
                _('trial_payment_success', lang_user),
                reply_markup=await balance_menu(person, lang_user)
            )
            if not await add_time_person(self.user_id, trial_duration_seconds):
                await self.message.answer(_('error_send_admin', lang_user))
                return
        else:
            if not await add_balance_person(
                    self.user_id,
                    total_amount
            ):
                await self.message.answer(_('error_send_admin', lang_user))
                return

            await self.message.answer(
                _('payment_success', lang_user).format(total_amount=total_amount),
                reply_markup=await balance_menu(person, lang_user)
            )
        
        await add_payment(
            self.user_id,
            total_amount,
            name_payment,
            payment_method_id
        )

        if CONFIG.auto_extension:
            await check_auto_renewal(
                person,
                self.message.bot,
                _('payment_autopay_text', lang_user)
            )
        if person.referral_user_tgid is not None:
            referral_user = person.referral_user_tgid
            referral_balance = (
                int(total_amount * (CONFIG.referral_percent * 0.01))
            )
            await add_referral_balance_person(
                referral_balance,
                referral_user
            )
            await self.message.bot.send_message(
                referral_user,
                _('reff_add_balance', await get_lang(referral_user)).format(
                    referral_balance=referral_balance
                )
            )
