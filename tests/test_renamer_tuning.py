import asyncio
from types import SimpleNamespace

import pytest

import pyrogram
import pyrogram.client as client_mod
import pyrogram.session.session as session_mod
from pyrogram import raw
from pyrogram.dispatcher import Dispatcher
from pyrogram.errors import FloodWait
from pyrogram.methods.rate_limiter import RateLimiter
from pyrogram.methods.utilities.start import enable_default_bot_rate_limiter
from pyrogram.session.session import Session
from tests.e2e import FakeDC, document, make_client as make_e2e_client
from tests.test_transfers import CHUNK, SIZE


class Asyncio:
    """asyncio stand-in that records sleep delays without advancing the clock."""

    def __init__(self, slept):
        self.slept = slept

    def __getattr__(self, name):
        return getattr(asyncio, name)

    async def sleep(self, delay, *args):
        if delay:
            self.slept.append(delay)
        await asyncio.sleep(0)


# ---------------------------------------------------------------- priority


async def test_priority_semaphore_serves_highest_priority_first():
    sem = client_mod.PrioritySemaphore(1)

    sem.acquire(0)  # hold the only slot (free slot: taken synchronously)
    assert sem.locked()

    order = []

    async def waiter(p, name):
        async with sem.acquire(p):
            order.append(name)
            await asyncio.sleep(0)

    tasks = [
        asyncio.ensure_future(waiter(0, "low")),
        asyncio.ensure_future(waiter(5, "high")),
        asyncio.ensure_future(waiter(1, "mid")),
    ]
    await asyncio.sleep(0)  # let all three enqueue
    await asyncio.sleep(0)

    for _ in range(3):
        sem.release()
        await asyncio.sleep(0)

    await asyncio.gather(*tasks)
    assert order == ["high", "mid", "low"], f"wake order {order}"


async def test_priority_semaphore_async_with_and_value():
    sem = client_mod.PrioritySemaphore(2)
    assert sem.value == 2 and not sem.locked()
    async with sem:
        assert sem.value == 1
    assert sem.value == 2


# ------------------------------------------------------- concurrency limits


def test_transfer_limits_split_and_env_tunable(monkeypatch):
    monkeypatch.setenv("VEKGRAM_MAX_CONCURRENT_DOWNLOADS", "3")
    monkeypatch.setenv("VEKGRAM_MAX_CONCURRENT_UPLOADS", "5")
    c = pyrogram.Client("limits", api_id=1, api_hash="x", in_memory=True)
    assert c.get_file_semaphore.value == 3
    assert c.save_file_semaphore.value == 5
    assert c.max_concurrent_transmissions == 16  # untouched fallback

    monkeypatch.delenv("VEKGRAM_MAX_CONCURRENT_DOWNLOADS")
    monkeypatch.delenv("VEKGRAM_MAX_CONCURRENT_UPLOADS")
    c2 = pyrogram.Client("limits2", api_id=1, api_hash="x", in_memory=True)
    assert c2.get_file_semaphore.value == 16
    assert c2.save_file_semaphore.value == 16


async def test_read_ahead_budget_is_shared_per_loop():
    c = pyrogram.Client("ra", api_id=1, api_hash="x", in_memory=True)
    assert c.read_ahead_slots is c.read_ahead_slots
    assert c.read_ahead_slots is client_mod.transfer_budget(
        client_mod.Client.MAX_READ_AHEAD_CHUNKS
    )


# ------------------------------------------------------------------- ping


async def test_media_sessions_ping_slower_than_main_session():
    class C:
        name = "t"

    main = Session(C(), 1, b"\x00" * 256, False)
    media = Session(C(), 1, b"\x00" * 256, False, is_media=True)
    cdn = Session(C(), 1, b"\x00" * 256, False, is_cdn=True)

    assert main.ping_interval == Session.PING_INTERVAL == 5
    assert media.ping_interval == Session.MEDIA_PING_INTERVAL == 30
    assert cdn.ping_interval == Session.MEDIA_PING_INTERVAL == 30


# -------------------------------------------------------------- dispatcher


def test_dispatcher_queue_size_from_env():
    import os
    old = os.environ.get("VEKGRAM_UPDATE_QUEUE")
    os.environ["VEKGRAM_UPDATE_QUEUE"] = "7"
    try:
        d = Dispatcher(SimpleNamespace())
        assert d.updates_queue.maxsize == 7
    finally:
        if old is None:
            os.environ.pop("VEKGRAM_UPDATE_QUEUE", None)
        else:
            os.environ["VEKGRAM_UPDATE_QUEUE"] = old


async def test_dropped_updates_are_counted():
    d = Dispatcher(SimpleNamespace())
    d.updates_queue = asyncio.Queue(maxsize=1)
    d.updates_queue.put_nowait(("u", {}, {}))

    # no workers running -> immediate drop
    assert await d.enqueue_update("u2", {}, {}) is False
    assert d.dropped_updates == 1

    # "workers exist" but the queue stays full -> ENQUEUE_TIMEOUT drop
    d.handler_worker_tasks = [object()]
    d.starting = True
    d.ENQUEUE_TIMEOUT = 0.05
    assert await d.enqueue_update("u3", {}, {}) is False
    assert d.dropped_updates == 2


# ------------------------------------------------------------ rate limiter


def test_bots_get_default_rate_limiter_users_do_not():
    bot = SimpleNamespace(rate_limiter=None, me=SimpleNamespace(is_bot=True))
    enable_default_bot_rate_limiter(bot)
    assert isinstance(bot.rate_limiter, RateLimiter)
    assert bot.rate_limiter._buckets["message"].rate == 20.0

    user = SimpleNamespace(rate_limiter=None, me=SimpleNamespace(is_bot=False))
    enable_default_bot_rate_limiter(user)
    assert user.rate_limiter is None

    preset = SimpleNamespace(rate_limiter=RateLimiter(), me=SimpleNamespace(is_bot=True))
    before = preset.rate_limiter
    enable_default_bot_rate_limiter(preset)
    assert preset.rate_limiter is before


# ------------------------------------------------------- download flood gate


class FloodDC(FakeDC):
    """FakeDC that answers the first `floods` GetFile calls with FLOOD_WAIT."""

    def __init__(self, file_size, floods, **kw):
        super().__init__(file_size, **kw)
        self.floods = floods
        self.getfile_calls = 0

    def _answer(self, query):
        inner = getattr(query, "query", query)
        if isinstance(inner, raw.functions.upload.GetFile):
            self.getfile_calls += 1
            if self.getfile_calls <= self.floods:
                raise FloodWait(value=5, rpc_name="upload.GetFile")
        return super()._answer(query)


async def test_download_flood_waits_are_gated_and_staggered(monkeypatch):
    slept = []
    # record sleeps from both levels that can answer a flooded GetFile:
    # workers invoke with sleep_threshold=0 (gate in client.get_file), the
    # first chunk with sleep_threshold=30 (gate in Session._invoke)
    monkeypatch.setattr(client_mod, "asyncio", Asyncio(slept))
    monkeypatch.setattr(session_mod, "asyncio", Asyncio(slept))

    dc = FloodDC(SIZE, floods=3, step=0)
    client = make_e2e_client(dc, sessions=4, premium=True)  # premium: no pacer sleeps

    async def stop():
        pass

    for session in await client._get_media_session_pool(2, 4):
        session.stop = stop

    total = 0
    async for chunk in client.get_file(document(), SIZE):
        total += len(chunk)

    assert total == SIZE
    assert dc.getfile_calls == SIZE // CHUNK + 3  # every chunk served, 3 of them flooded first
    flood_sleeps = [s for s in slept if 4 <= s <= 6]
    assert len(flood_sleeps) == 3, (
        f"slept {slept}; each of the 3 flooded GetFile calls must wait ~5s "
        "(armed gate deadline +- clock epsilon, plus up to 1s jitter)"
    )
    assert all(4 <= s <= 6 for s in slept), slept
