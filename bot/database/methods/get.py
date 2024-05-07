from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy import and_, select, func, desc

from bot.database.main import engine
from bot.database.models.main import (
    Persons,
    Servers,
    Payments,
    StaticPersons,
    PromoCode,
    WithdrawalRequests
)
from bot.misc.util import CONFIG


async def get_person(telegram_id):
    async with AsyncSession(autoflush=False, bind=engine()) as db:
        statement = select(Persons).filter(Persons.tgid == telegram_id)
        result = await db.execute(statement)
        person = result.scalar_one_or_none()
        return person


async def get_person_id(list_input):
    async with AsyncSession(autoflush=False, bind=engine()) as db:
        statement = select(Persons).filter(Persons.tgid.in_(list_input))
        result = await db.execute(statement)
        persons = result.scalars().all()
        return persons


async def _get_person(db, tgid):
    statement = select(Persons).filter(Persons.tgid == tgid)
    result = await db.execute(statement)
    person = result.scalar_one_or_none()
    return person


async def _get_server(db, name):
    statement = select(Servers).filter(Servers.name == name)
    result = await db.execute(statement)
    server = result.scalar_one_or_none()
    return server


async def get_all_user():
    async with AsyncSession(autoflush=False, bind=engine()) as db:
        statement = select(Persons)
        result = await db.execute(statement)
        persons = result.scalars().all()
        return persons


async def get_all_subscription():
    async with AsyncSession(autoflush=False, bind=engine()) as db:
        statement = select(Persons).filter(Persons.banned == 0)
        result = await db.execute(statement)
        persons = result.scalars().all()
        return persons


async def get_no_subscription():
    async with AsyncSession(autoflush=False, bind=engine()) as db:
        statement = select(Persons).filter(Persons.banned == 1)
        result = await db.execute(statement)
        persons = result.scalars().all()
        return persons


async def get_payments():
    async with AsyncSession(autoflush=False, bind=engine()) as db:
        statement = select(Payments).options(
            joinedload(Payments.payment_id)
        )
        result = await db.execute(statement)
        payments = result.scalars().all()

        for payment in payments:
            payment.user = payment.payment_id.username

        return payments


async def get_all_server():
    async with AsyncSession(autoflush=False, bind=engine()) as db:
        statement = select(Servers)
        result = await db.execute(statement)
        servers = result.scalars().all()
        return servers


async def get_server(name):
    async with AsyncSession(autoflush=False, bind=engine()) as db:
        return await _get_server(db, name)


async def get_server_id(id_server):
    async with AsyncSession(autoflush=False, bind=engine()) as db:
        statement = select(Servers).filter(Servers.id == id_server)
        result = await db.execute(statement)
        server = result.scalar_one_or_none()
        return server


async def get_free_server():
    async with AsyncSession(autoflush=False, bind=engine()) as db:
        statement = select(Servers).filter(
            and_(
                Servers.space < int(CONFIG.max_people_server),
                Servers.work == 1
            )
        )
        result = await db.execute(statement)
        server = result.scalar_one_or_none()

        if server is None:
            raise Exception('Server not found')

        return server


async def get_free_servers():
    async with AsyncSession(autoflush=False, bind=engine()) as db:
        statement = select(Servers).filter(
            and_(
                Servers.space < int(CONFIG.max_people_server),
                Servers.work == 1
            )
        )
        result = await db.execute(statement)
        servers = result.scalars().all()
        if not servers:
            raise Exception('Server not found')
        return servers


async def get_all_static_user():
    async with AsyncSession(autoflush=False, bind=engine()) as db:
        statement = select(StaticPersons).options(
            joinedload(StaticPersons.server_table)
        )
        result = await db.execute(statement)
        all_static_user = result.scalars().all()
        return all_static_user


async def get_all_promo_code():
    async with AsyncSession(autoflush=False, bind=engine()) as db:
        statement = select(PromoCode)
        result = await db.execute(statement)
        promo_code = result.scalars().all()
        return promo_code


async def get_promo_code(text_promo):
    async with AsyncSession(autoflush=False, bind=engine()) as db:
        statement = select(PromoCode).options(
            joinedload(PromoCode.person)
        ).filter(
            PromoCode.text == text_promo
        )
        result = await db.execute(statement)
        promo_code = result.unique().scalar_one_or_none()
        return promo_code


async def get_count_referral_user(tgid):
    async with AsyncSession(autoflush=False, bind=engine()) as db:
        statement = select(func.count(Persons.id)).filter(
            Persons.referral_user_tgid == tgid
        )
        result = await db.execute(statement)
        return result.scalar()


async def get_referral_balance(tgid):
    async with AsyncSession(autoflush=False, bind=engine()) as db:
        statement = select(Persons).filter(Persons.tgid == tgid)
        result = await db.execute(statement)
        person = result.scalar_one_or_none()
        return person.referral_balance


async def get_all_application_referral():
    async with AsyncSession(autoflush=False, bind=engine()) as db:
        statement = select(WithdrawalRequests)
        result = await db.execute(statement)
        return result.scalars().all()


async def get_application_referral_check_false():
    async with AsyncSession(autoflush=False, bind=engine()) as db:
        statement = select(WithdrawalRequests).filter(
            WithdrawalRequests.check_payment == 0
        )
        result = await db.execute(statement)
        return result.scalars().all()


async def get_person_lang(telegram_id):
    async with AsyncSession(autoflush=False, bind=engine()) as db:
        statement = select(Persons).filter(Persons.tgid == telegram_id)
        result = await db.execute(statement)
        person = result.scalar_one_or_none()
        if person is None:
            return CONFIG.languages
        return person.lang


def need_to_renew_subscription(user):
    return user.subscription < time.time()

async def get_payment_method_id(user_id):
    async with AsyncSession(autoflush=False, bind=engine()) as db:
        statement = select(Payments.payment_method_id).filter(Payments.user == user_id).order_by(desc(Payments.data)).limit(1)
        result = await db.execute(statement)
        payment_method = result.scalar_one_or_none()
        return payment_method


async def get_last_payment(user_id):
    async with AsyncSession(autoflush=False, bind=engine()) as db:
        statement = select(Payments).where(Payments.user == user_id).order_by(desc(Payments.data)).limit(1)
        result = await db.execute(statement)
        last_payment = result.scalar_one_or_none()
        return last_payment


