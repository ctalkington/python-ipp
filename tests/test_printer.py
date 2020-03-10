"""Tests for Printer."""
import pytest

from aiohttp import ClientSession, TCPConnector

from ipp import IPP, Printer
from tests import DEFAULT_PRINTER_URI, FakeIPPServer, FakeResolver

@pytest.fixture()
async def info(event_loop):
    fake_ipp = FakeIPPServer(loop=event_loop)
    info = await fake_ipp.start()
    yield info
    await fake_ipp.stop()


@pytest.fixture()
async def session(event_loop, info):
    resolver = FakeResolver(info, loop=event_loop)
    connector = TCPConnector(loop=event_loop, resolver=resolver, verify_ssl=False)
    session = ClientSession(connector=connector, loop=event_loop)
    yield session
    await session.close()


def test_init(session) -> None:
    instance = Printer(DEFAULT_PRINTER_URI)
    assert isinstance(instance, Printer)
    assert isinstance(instance.ipp, IPP)


@pytest.mark.asyncio
async def test_get_attributes(session) -> None:
    instance = Printer(DEFAULT_PRINTER_URI, session=session)
    attributes = await instance.get_attributes()

    assert attributes == {}


@pytest.mark.asyncio
async def test_get_jobs() -> None:
    instance = Printer(DEFAULT_PRINTER_URI, session=session)
    jobs = await instance.get_jobs()

    assert jobs == {}
