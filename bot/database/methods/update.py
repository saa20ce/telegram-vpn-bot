import time

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from bot.database.main import engine
from bot.database.methods.get import _get_person, _get_server
from bot.database.models.main import Persons, WithdrawalRequests


async def add_balance_person(tgid, deposit):
    async with AsyncSession(autoflush=False, bind=engine()) as db:
        person = await _get_person(db, tgid)
        if person is not None:
            person.balance += int(deposit)
            await db.commit()
            return True
        return False


async def reduce_balance_person(deposit, tgid):
    async with AsyncSession(autoflush=False, bind=engine()) as db:
        person = await _get_person(db, tgid)
        if person is not None:
            person.balance -= int(deposit)
            await db.commit()
            return True
        return False


async def reduce_referral_balance_person(amount, tgid):
    async with AsyncSession(autoflush=False, bind=engine()) as db:
        person = await _get_person(db, tgid)
        if person is not None:
            person.referral_balance -= int(amount)
            if person.referral_balance < 0:
                return False
            await db.commit()
            return True
        return False


async def update_balance_person(amount, tgid):
    async with AsyncSession(autoflush=False, bind=engine()) as db:
        person = await _get_person(db, tgid)
        if person is not None:
            person.balance = int(amount)
            if person.balance < 0:
                return False
            await db.commit()
            return True
        return False


async def add_referral_balance_person(amount, tgid):
    async with AsyncSession(autoflush=False, bind=engine()) as db:
        person = await _get_person(db, tgid)
        if person is not None:
            person.referral_balance += int(amount)
            await db.commit()
            return True
        return False


async def add_time_person(tgid, count_time):
    async with AsyncSession(autoflush=False, bind=engine()) as db:
        person = await _get_person(db, tgid)
        if person is not None:
            now_time = int(time.time()) + count_time
            if person.banned:
                person.subscription = int(now_time)
                person.banned = False
            else:
                person.subscription += count_time
            await db.commit()
            return True
        return False


async def person_banned_true(tgid):
    async with AsyncSession(autoflush=False, bind=engine()) as db:
        person = await _get_person(db, tgid)
        if person is not None:
            person.server = None
            person.banned = True
            person.notion_oneday = False
            person.subscription = int(time.time())
            await db.commit()
            return True
        return False


async def person_one_day_true(tgid):
    async with AsyncSession(autoflush=False, bind=engine()) as db:
        person = await _get_person(db, tgid)
        if person is not None:
            person.notion_oneday = True
            await db.commit()
            return True
        return False


async def person_delete_server(tgid):
    async with AsyncSession(autoflush=False, bind=engine()) as db:
        person = await _get_person(db, tgid)
        if person is not None:
            person.server = None
            await db.commit()
            return True
        return False


async def server_work_update(name, work):
    async with AsyncSession(autoflush=False, bind=engine()) as db:
        server = await _get_server(db, name)
        if server is not None:
            server.work = work
            await db.commit()
            return True
        return False


async def server_space_update(name, new_space):
    async with AsyncSession(autoflush=False, bind=engine()) as db:
        server = await _get_server(db, name)
        if server is not None:
            server.space = new_space
            await db.commit()
            return True
        return False


async def add_user_in_server(telegram_id, server):
    async with AsyncSession(autoflush=False, bind=engine()) as db:
        person = await db.execute(
            select(Persons).filter(Persons.tgid == telegram_id)
        )
        person = person.scalar_one_or_none()
        person.server = server.id
        await db.commit()


async def add_pomo_code_person(tgid, promo_code):
    async with AsyncSession(autoflush=False, bind=engine()) as db:
        async with db.begin():
            statement = select(Persons).options(
                joinedload(Persons.promocode)).filter(Persons.tgid == tgid)
            result = await db.execute(statement)
            person = result.unique().scalar_one_or_none()

            if person is not None:
                person.balance += int(promo_code.add_balance)
                person.promocode.append(promo_code)
                await db.commit()
                return True
            return False


async def succes_aplication(id_application):
    async with AsyncSession(autoflush=False, bind=engine()) as db:
        application = await db.execute(
            select(WithdrawalRequests)
            .filter(WithdrawalRequests.id == id_application)
        )
        application_instance = application.scalar_one_or_none()
        if application_instance is not None:
            application_instance.check_payment = True
            await db.commit()
            return True
        return False


async def update_delete_users_server(server):
    async with AsyncSession(autoflush=False, bind=engine()) as db:
        await db.execute(
            update(Persons)
            .where(Persons.server == server.id)
            .values({"server": None})
        )
        await db.commit()


async def update_lang(lang, tgid):
    async with AsyncSession(autoflush=False, bind=engine()) as db:
        person = await _get_person(db, tgid)
        if person is not None:
            person.lang = lang
            await db.commit()
            return True
        return False


async def update_person_recurring_status(tgid, status):
    async with AsyncSession(autoflush=False, bind=engine()) as db:
        await db.execute(
            update(Persons)
            .where(Persons.tgid == tgid)
            .values(recurring_payment_status=status)
        )
        await db.commit()

