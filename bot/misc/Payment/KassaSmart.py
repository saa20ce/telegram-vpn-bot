import asyncio
import uuid

from yookassa import Configuration, Payment

from bot.database.methods.get import get_person
from bot.keyboards.inline.user_inline import pay_and_check
from bot.misc.Payment.payment_systems import PaymentSystem
from bot.misc.language import Localization, get_lang
from bot.database.methods.update import (
    add_balance_person,
    update_person_recurring_status
)

import logging
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
handler = logging.FileHandler("KassaSmart.log", encoding='utf-8')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
log.addHandler(handler)

_ = Localization.text


class KassaSmart(PaymentSystem):
    CHECK_ID: str = None
    ID: str = None
    EMAIL: str

    def __init__(self,
                 config,
                 message,
                 user_id,
                 price,
                 email=None,
                 recurring_payment_amount=None):
        super().__init__(message, user_id, price)
        self.ACCOUNT_ID = int(config.yookassa_shop_id)
        self.SECRET_KEY = config.yookassa_secret_key
        self.EMAIL = email
        self.recurring_payment_amount = recurring_payment_amount

    async def create(self):
        self.ID = str(uuid.uuid4())

    async def successful_payment(self, total_amount, name_payment, payment_method_id=None):
        # Вызов оригинального метода successful_payment из базового класса
        await super().successful_payment(total_amount, name_payment, payment_method_id)
        await update_person_recurring_status(self.user_id, True)
        person = await get_person(self.user_id)
        if not person:
            await self.message.answer(_('error_person_not_found', lang_user))
            return
        log.debug(f"Person recurring_payment_status User ID={person.recurring_payment_status}")

    async def check_payment(self, time):
        #log.debug("Checking payment")
        Configuration.account_id = self.ACCOUNT_ID
        Configuration.secret_key = self.SECRET_KEY
        tic = 0
        is_payment_processed = False
        while tic < time and not is_payment_processed:
            try:
                res = Payment.list().items
                #log.debug(f"Received payment items: {res}")
                for item in res:
                    if item.status == 'succeeded' and item.id == self.ID:
                        await self.successful_payment(
                            self.price,
                            'YooKassaSmart',
                            item.payment_method.id
                        )
                        is_payment_processed = True
                        #log.info(f'Successfull ayment_method.id: {item.payment_method.id}')
                        return
            except Exception as e:
                log.error(f"Error checking payment: {e} , Payment ID: {self.ID}")
                break
            if is_payment_processed:
                break
            tic += self.STEP
            await asyncio.sleep(self.STEP)
        #log.info("Exiting payment check loop.")
        return

    async def invoice(self, lang_user):
        payment = Payment.create({
            "amount": {
              "value": self.price,
              "currency": "RUB"
            },
            "receipt": {
                "customer": {
                    "full_name": self.message.from_user.full_name,
                    "email": self.EMAIL,
                },
                "items": [
                    {
                        "description": _('description_payment', lang_user),
                        "quantity": "1.00",
                        "amount": {
                            "value": self.price,
                            "currency": "RUB"
                        },
                        "vat_code": "2",
                        "payment_mode": "full_payment",
                    },
                ]
            },
            "confirmation": {
              "type": "redirect",
              "return_url": "https://t.me/"
            },
            "capture": True,
            "description": _('description_payment', lang_user),
            "save_payment_method": True
        }, self.ID)
        self.ID = payment.id
        return payment.confirmation.confirmation_url

    async def to_pay(self):
        await self.create()
        Configuration.account_id = self.ACCOUNT_ID
        Configuration.secret_key = self.SECRET_KEY
        lang_user = await get_lang(self.user_id)
        link_invoice = await self.invoice(lang_user)
        await self.message.answer(
            _('payment_balance_text', lang_user).format(price=self.price),
            reply_markup=await pay_and_check(link_invoice, lang_user)
        )
        # log.info(
        #     f'Create payment link YooKassaSmart '
        #     f'User: (ID: {self.user_id}'
        # )
        try:
            await self.check_payment(self.TEN_MINUTE)
        except Exception as e:
            log.error(f"{e} - The payment period has expired")

    async def create_recurring_payment(self, payment_method_id):
        Configuration.account_id = self.ACCOUNT_ID
        Configuration.secret_key = self.SECRET_KEY
        log.debug(f"Creating recurring payment: User ID={self.user_id}, Payment Method ID={payment_method_id}, Amount={self.recurring_payment_amount}")

        payment = Payment.create({
            "amount": {
                "value": str(self.recurring_payment_amount),
                "currency": "RUB"
            },
            "payment_method_id": payment_method_id,
            "capture": True,
            "description": "Рекуррентный платеж за использование сервиса"
        })

        for _ in range(10):  # Повторяем проверку 10 раз с интервалом в 30 секунд
            payment = Payment.find_one(payment.id)
            person = await get_person(self.user_id)
            if not person:
                await self.message.answer(_('error_person_not_found', lang_user))
                return
            if payment.status == 'succeeded':
                await add_balance_person(person.tgid, self.recurring_payment_amount)
                log.info(f"Recurring payment successful for User ID: {self.user_id}, Amount: {self.recurring_payment_amount}")
                break
            elif payment.status in ['pending', 'waiting_for_capture']:
                await asyncio.sleep(30)  # Ждём 30 секунд перед следующей проверкой
            else:
                log.error(f"Failed to create recurring payment for User ID: {self.user_id}, Payment Status: {payment.status}")
                break

        return payment

    def __str__(self):
        return 'YooKassaSmart payment system'
