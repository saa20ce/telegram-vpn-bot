import logging

logging.basicConfig(
        level=logging.DEBUG,
        format="%(levelname)s %(filename)s:%(lineno)d [%(asctime)s] - %(name)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("debug.log", encoding='utf-8')
        ]
    )

from bot.main import start_bot
import asyncio

if __name__ == '__main__':
    asyncio.run(start_bot())
