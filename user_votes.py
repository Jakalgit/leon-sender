import asyncio
import logging
import time

from logs import logger

user_votes: dict[int, tuple[set[int], float]] = {}


async def cleanup_old_votes():
    while True:
        now = time.time()
        to_delete = []

        ttl = 2 * 24 * 60 * 60

        for message_id, (_, created_at) in user_votes.items():
            if now - created_at > ttl:
                to_delete.append(message_id)

        for mid in to_delete:
            del user_votes[mid]
            logger.log(msg=f"[CLEANUP] Удалена запись message_id={mid}", level=logging.INFO)

        await asyncio.sleep(3600)