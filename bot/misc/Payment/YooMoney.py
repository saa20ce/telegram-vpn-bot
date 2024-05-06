import asyncio
import logging
import uuid

from yoomoney import Quickpay, Client

from bot.keyboards.inline.user_inline import pay_and_check
from bot.misc.Payment.payment_systems import PaymentSystem
from bot.misc.language import get_lang, Localization

log = logging.getLogger(__name__)

_ = Localization.text


class YooMoney(PaymentSystem):
    CHECK_ID: str = None
    ID: str = None

    def __init__(self, config, message, user_id, price, check_id=None):
        super().__init__(message, user_id, price)
        self.TOKEN = config.yoomoney_token
        self.TOKEN_WALLET = config.yoomoney_wallet_token

    async def create(self):
        self.ID = str(uuid.uuid4())

    async def check_payment(self, time):
        client = Client(self.TOKEN)
        tic = 0
        while tic < time:
            history = client.operation_history(label=self.ID)
            for operation in history.operations:
                await self.successful_payment(self.price, 'YooMoney')
                return
            tic += self.STEP
            await asyncio.sleep(self.STEP)
        return

    async def invoice(self):
        quick_pay = Quickpay(
            receiver=self.TOKEN_WALLET,
            quickpay_form='shop',
            targets='Deposit balance',
            paymentType='SB',
            sum=self.price,
            label=self.ID
        )
        return quick_pay.base_url

    async def to_pay(self):
        lang_user = await get_lang(self.user_id)
        await self.message.delete()
        await self.create()
        link_invoice = await self.invoice()
        await self.message.answer(
            _('payment_balance_text', lang_user).format(price=self.price),
            reply_markup=await pay_and_check(link_invoice, lang_user)
        )
        log.info(
            f'Create payment link YooMoney '
            f'User: {self.user_id}'
        )
        try:
            await self.check_payment(self.TEN_MINUTE)
        except Exception as e:
            log.error(e, 'The payment period has expired')

    def __str__(self):
        return 'Платежная система YooMoney'
