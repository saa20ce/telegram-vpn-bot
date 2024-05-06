import asyncio
import logging
import uuid

from WalletPay import AsyncWalletPayAPI

from bot.keyboards.inline.user_inline import wallet_pay
from bot.misc.Payment.payment_systems import PaymentSystem
from bot.misc.language import get_lang, Localization

log = logging.getLogger(__name__)

_ = Localization.text


class WalletPay(PaymentSystem):
    WALLET: type(AsyncWalletPayAPI)
    ONE_MINUTE = 60

    def __init__(self, config, message, user_id, price, data=None):
        super().__init__(message, user_id, price)
        self.WALLET = AsyncWalletPayAPI(api_key=config.tg_wallet_token)

    async def new_order(self, lang_user):
        order = await self.WALLET.create_order(
            amount=self.price,
            currency_code="RUB",
            description=_('description_payment', lang_user),
            external_id=str(uuid.uuid4()),
            timeout_seconds=60,
            customer_telegram_user_id=self.user_id
        )
        return order

    async def check_pay_wallet(self, order, time):
        tic = 0
        while tic < time:
            order_preview = await self.WALLET.get_order_preview(
                order_id=order.id)
            if order_preview.status == "PAID":
                await self.successful_payment(
                    self.price,
                    'WalletPay'
                )
                return
            tic += 2
            await asyncio.sleep(2)
        return

    async def to_pay(self):
        lang_user = await get_lang(self.user_id)
        await self.message.delete()
        order = await self.new_order(lang_user)
        await self.message.answer(
            _('payment_balance_text', lang_user).format(price=self.price),
            reply_markup=await wallet_pay(order, lang_user)
        )
        log.info(
            f'Create payment link WalletPay '
            f'User: ID: {self.user_id}'
        )
        try:
            await self.check_pay_wallet(order, self.ONE_MINUTE)
        except Exception as e:
            log.error(e, 'The payment period has expired')

    def __str__(self):
        return 'Платежная система WalletPay'
