import datetime
import time

from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.main import engine
from bot.database.methods.get import _get_person
from bot.database.models.main import (
    Persons,
    Payments,
    StaticPersons,
    PromoCode,
    WithdrawalRequests
)


async def add_new_person(from_user, username, subscription, ref_user):
    async with AsyncSession(autoflush=False, bind=engine()) as db:
        tom = Persons(
            tgid=from_user.id,
            username=username,
            fullname=from_user.full_name,
            subscription=int(time.time()) + subscription,
            referral_user_tgid=ref_user or None
        )
        db.add(tom)
        await db.commit()


async def add_payment(tgid, deposit, payment_system, payment_method_id=None):
    async with AsyncSession(autoflush=False, bind=engine()) as db:
        person = await _get_person(db, tgid)
        if person is not None:
            payment = Payments(
                amount=deposit,
                data=datetime.datetime.now(),
                payment_system=payment_system,
                payment_method_id=payment_method_id
            )
            payment.user = person.id
            db.add(payment)
            await db.commit()


async def add_server(server):
    async with AsyncSession(autoflush=False, bind=engine()) as db:
        db.add(server)
        await db.commit()


async def add_static_user(name, server):
    async with AsyncSession(autoflush=False, bind=engine()) as db:
        static_user = StaticPersons(
            name=name,
            server=server
        )
        db.add(static_user)
        await db.commit()


async def add_promo(text_promo, add_balance):
    async with AsyncSession(autoflush=False, bind=engine()) as db:
        promo_code = PromoCode(
            text=text_promo,
            add_balance=add_balance
        )
        db.add(promo_code)
        await db.commit()


async def add_withdrawal(tgid, amount, payment_info, communication):
    async with AsyncSession(autoflush=False, bind=engine()) as db:
        withdrawal = WithdrawalRequests(
            amount=amount,
            payment_info=payment_info,
            user_id=tgid,
            communication=communication
        )
        db.add(withdrawal)
        await db.commit()
