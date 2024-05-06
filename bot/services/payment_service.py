from bot.misc.Payment.KassaSmart import KassaSmart
from bot.misc.util import CONFIG

class PaymentService:
    def __init__(self, config, user_id, payment_method_id, amount):
        self.config = config
        self.user_id = user_id
        self.payment_method_id = payment_method_id
        self.amount = amount

    async def create_recurring_payment(self):
        from bot.misc.Payment.KassaSmart import KassaSmart
        kassa_smart = KassaSmart(
            config=self.config,
            message=None,
            user_id=self.user_id,
            price=CONFIG.recurring_payment_amount,
            email=None,
            recurring_payment_amount=CONFIG.recurring_payment_amount
        )
        return await kassa_smart.create_recurring_payment(self.payment_method_id)

