#import logging
import time
from datetime import datetime, timedelta, timezone

from aiogram import Bot

from bot.keyboards.reply.user_reply import user_menu
from bot.database.methods.get import (
    get_all_subscription,
    get_all_user,
    get_server_id,
    get_person,
    get_last_payment,
    get_payment_method_id,
)
from bot.database.methods.update import (
    person_banned_true,
    person_one_day_true,
    server_space_update,
    add_time_person,
    reduce_balance_person,
)
from bot.misc.VPN.ServerManager import ServerManager
from bot.misc.language import Localization, get_lang
from bot.misc.util import CONFIG


#log = logging.getLogger(__name__)

import logging
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
handler = logging.FileHandler("loop.log", encoding='utf-8')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
log.addHandler(handler)

_ = Localization.text

COUNT_SECOND_DAY = 86400

month_count = {
    CONFIG.month_cost[2]: 6,
    CONFIG.month_cost[1]: 3,
    CONFIG.month_cost[0]: 1,
}


async def loop(bot: Bot):
    try:
        all_persons = await get_all_user()
        for person in all_persons:
            await check_date(person, bot)
    except Exception as e:
        log.error(e)


async def check_date(person, bot: Bot):
    try:
        if person.subscription <= int(time.time()):
            if person.recurring_payment_status == True:
                log.debug(f"Recurring person: {len(person.username)}")
                log.info(f"Processing recurrent payment for user {person.id}")
                payment_method_id = await get_payment_method_id(person.id)

                from bot.services.payment_service import PaymentService
                payment_service = PaymentService(CONFIG, person.tgid, payment_method_id, CONFIG.recurring_payment_amount)
                payment = await payment_service.create_recurring_payment()
                if payment.status == 'succeeded':
                    await bot.send_message(
                        person.tgid,
                        _('loop_autopay', person.lang).format(
                            text=_('payment_autopay_text', person.lang),
                            mount_count=1
                        ),
                        reply_markup=await user_menu(
                            person,
                            person.lang
                        )
                    )
                    log.info(f"Successfully paid recurring payment for person ID: {person.id}")
                else:
                    log.error(f"Failed to create recurring payment for person ID: {person.id}")

            if await check_auto_renewal(
                    person,
                    bot
            ):
                return
            if person.server is not None:
                await delete_key(person)
            await person_banned_true(person.tgid)
            await bot.send_message(
                person.tgid,
                _('ended_sub_message', person.lang),
                reply_markup=await user_menu(person, person.lang)
            )
        elif (person.subscription <= int(time.time()) + COUNT_SECOND_DAY
              and not person.notion_oneday):
            await person_one_day_true(person.tgid)
            await bot.send_message(
                person.tgid,
                _('alert_to_renew_sub', person.lang)
            )
        return
    except Exception as e:
        log.error(e, "Error in the user date verification cycle")
        return


async def delete_key(person):
    server = await get_server_id(person.server)
    server_manager = ServerManager(server)
    try:
        if await server_manager.delete_client(person.tgid):
            all_client = await server_manager.get_all_user()
        else:
            raise Exception("Couldn't delete it")
    except Exception as e:
        log.error(e, "Failed to connect to the server")
        raise e
    space = len(all_client)
    if not await server_space_update(server.name, space):
        raise "Failed to update data about free space on the server"


async def check_auto_renewal(person, bot):
    try:
        for price, mount_count in month_count.items():
            if person.balance >= price:
                if await add_time_person(
                        person.tgid,
                        mount_count * CONFIG.COUNT_SECOND_MOTH
                ):
                    await reduce_balance_person(
                        price,
                        person.tgid
                    )
                    return True
                else:
                    await bot.send_message(
                        CONFIG.admin_tg_id,
                        _(
                            'loop_autopay_error',
                            await get_lang(CONFIG.admin_tg_id)
                        ).format(telegram_id=person.tgid)
                    )
    except Exception as e:
        log.error(
            f'{e} Error when trying '
            f'to auto-renew a subscription to '
            f'a client {person.username} {person.tgid}'
        )
    return False

