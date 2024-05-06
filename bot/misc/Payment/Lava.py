import asyncio
import hashlib
import hmac
import json
import logging
import random
import secrets
import time

import aiohttp

from bot.keyboards.inline.user_inline import pay_and_check
from bot.misc.Payment.payment_systems import PaymentSystem
from bot.misc.language import Localization, get_lang

log = logging.getLogger(__name__)

_ = Localization.text


class Lava(PaymentSystem):
    CHECK_ID: str = None
    ID: str = None

    def __init__(self, config, message, user_id, price, check_id=None):
        super().__init__(message, user_id, price)
        self.CHECK_ID = check_id
        self.shop_id = config.lava_id_project
        self.secret = config.lava_token_secret
        self.base_url = "https://api.lava.ru/"
        self.timeout = aiohttp.ClientTimeout(total=360)

    def _signature_headers(self, data):
        json_str = json.dumps(data).encode()
        sign = hmac.new(
            bytes(self.secret, 'UTF-8'),
            json_str,
            hashlib.sha256
        ).hexdigest()
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Signature': sign
        }
        return headers

    async def create_invoice(self, lang_user) -> dict:
        url = f"{self.base_url}/business/invoice/create"
        params = {
            "sum": self.price,
            "shopId": self.shop_id,
            "orderId":
                f'{time.time()}_{secrets.token_hex(random.randint(5, 10))}',
            "comment": _('payment_balance_text2', lang_user)
            .format(price=self.price)
        }
        headers = self._signature_headers(params)
        async with aiohttp.ClientSession(
                headers=headers,
                timeout=self.timeout
        ) as session:
            response = await session.post(
                url=url, headers=headers,
                json=params
            )
            res = await response.json()
            await session.close()
            return res

    async def status_invoice(self) -> bool:
        url = f"{self.base_url}/business/invoice/status"
        params = {
            "shopId": self.shop_id,
            "invoiceId": self.CHECK_ID
        }
        headers = self._signature_headers(params)
        async with aiohttp.ClientSession(
                headers=headers,
                timeout=self.timeout
        ) as session:
            response = await session.post(
                url=url,
                headers=headers,
                json=params
            )
            res = await response.json()
            await session.close()
            if res['data']['status'] == "success":
                return True
            else:
                return False

    async def check_payment(self, time):
        tic = 0
        while tic < time:
            if await self.status_invoice():
                await self.successful_payment(self.price, 'Lava')
                return
            tic += self.STEP
            await asyncio.sleep(self.STEP)
        return

    async def to_pay(self):
        lang_user = await get_lang(self.user_id)
        await self.message.delete()
        invoice = await self.create_invoice(lang_user)
        link = invoice['data']['url']
        self.CHECK_ID = invoice['data']['id']
        await self.message.answer(
            _('payment_balance_text', lang_user).format(price=self.price),
            reply_markup=await pay_and_check(link, lang_user)
        )
        log.info(
            f'Create payment link Lava '
            f'User: ID: {self.user_id}'
        )
        try:
            await self.check_payment(self.TEN_MINUTE)
        except Exception as e:
            log.error(e, 'The payment period has expired')

    def __str__(self):
        return 'Lava payment system'
