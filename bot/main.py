import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.strategy import FSMStrategy
from aiogram.enums import ParseMode
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from bot.misc.env import TgKeys
from bot.handlers.user.main import user_router
from bot.handlers.admin.main import admin_router
from bot.database.models.main import create_all_table
from bot.misc.commands import set_commands
from bot.misc.loop import (loop)
from bot.misc.util import CONFIG

log = logging.getLogger(__name__)

async def start_bot():
    log.info("Starting the bot.")
    dp = Dispatcher(
        storage=MemoryStorage(),
        fsm_strategy=FSMStrategy.USER_IN_CHAT
    )
    # todo Register all the routers from handlers package
    dp.include_routers(
        user_router,
        admin_router
    )

    await create_all_table()
    scheduler = AsyncIOScheduler()
    bot = Bot(token=TgKeys.TOKEN, parse_mode=ParseMode.HTML)
    await set_commands(bot)
    jobs = scheduler.get_jobs()
    for job in jobs:
        log.debug(f"Job: {job.name} | Next Run: {job.next_run_time} | Interval: {job.trigger}")
    scheduler.add_job(loop, "interval", seconds=15, args=(bot,))
    scheduler.start()
    await dp.start_polling(bot)

